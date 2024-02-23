# Redemption project

This is the Redemption of False Positives project.

## Copyright

<legal>
'Redemption' Automated Code Repair Tool
Copyright 2023, 2024 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
INFRINGEMENT.
Licensed under a MIT (SEI)-style license, please see License.txt or
contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public
release and unlimited distribution.  Please see Copyright notice for
non-US Government use and distribution.
This Software includes and/or makes use of Third-Party Software each
subject to its own license.
DM23-2165
</legal>

## Build instructions

The code is designed to run inside a Docker container, which means you will need Docker. To build the Docker container:

```sh
docker  build  -f Dockerfile.prereq  -t docker.cc.cert.org/redemption/prereq  .
```

This image contains all the dependencies needed to run the repair tool. (It does not actually contain the repair tool itself.)

This command starts a Bash shell in the container:

```sh
docker run -it --rm -v ${PWD}:/host -w /host docker.cc.cert.org/redemption/prereq  bash
```

### Simple Sanity Test

The tool has a simple sanity test that you can run in the `prereq` container. It uses pytest to run all the tests in the `/host/code/acr/test` directory of the container (all in functions with names starting with `test_`) To run these tests:

```sh
pushd /host/code/acr/test
pytest
```

All tests should pass.

### Docker Container `test`

There is a `test` Docker container that you can build and test with. It builds `git` and `zeek`. Building zeek takes about 40 minutes on one machine.  To build and run the `test` container:

```sh
docker  build  -f Dockerfile.test  -t docker.cc.cert.org/redemption/test  .
docker run -it --rm -v ${PWD}:/host -w /host docker.cc.cert.org/redemption/test  bash
```

## Running the Redemption Tool

For a simple demo example of running the tool, see the [simple demo example](doc/examples/simple/README.md).

### Static Analysis

The Redemption Tool presumes that you have static-analysis (SA) tool output.  It currently supports three SA tools:  `clang_tidy_oss` or `cppcheck_oss` or `rosecheckers_oss`. Each SA tool should produce a file with the alerts it generated. If `$TOOL` represents your tool, instructions for generating the alerts file live in `data/$TOOL/$TOOL.md`.  We will assume you have run the tool, and created the alerts file, which we will call `alerts.txt`. (The actual file need not be a text file).  Finally, when you produced your SA output, the code you ran was in a directory which we'll call the `$BASE_DIR`.

### Convert to Input

Next, you must convert the `alerts.txt` format into a simple JSON format that the redemption tool understands. The `alerts2input.py` file produces suitable JSON files. So you must run this script first; it will create the `alerts.json` file with the alerts you will use.

``` sh
python3 /host/code/analysis/alerts2input.py  $BASE_DIR  clang_tidy_oss  alerts.txt  alerts.json
```

For example, the `test` Docker container contains the source code for Git, as well as Cppcheck output.  So you can convert Cppcheck's output to alerts using this script:

``` sh
python3 /host/code/analysis/alerts2input.py  /oss/git  cppcheck_oss  /host/data/cppcheck/git/cppcheck.xml  ./alerts.json
```

### Manually-generated Input

The `alerts.json` file is a straightforward JSON file, and one can be created manually. This file consists of a list of alerts, each list element describes one alert. Each alert is a map with the following keys:

 * tool: The static-analysis tool reporting the alert
 * file: The source file to repair. May be a header (`.h`) file
 * line: Line number reported by tool
 * column: (Optional) Column number reported by tool
 * message: String message reported by tool
 * checker: The checker (that is, component of the SA tool) that reported the alert
 * rule: The CERT rule that the alert rules is being violated

Of these, the file, line and rule fields are the only strictly required fields. However, the column and message fields are helpful if the file and line are not sufficient to identify precisely which code is being reported.   Be warned that due to inconsistencies between the way different SA tools report alerts, our tool may misinterpret a manually-generated alert. The best way to ensure your alert is interpreted correctly is to fashion it to be as similar as possible to an alert generated by clang_tidy or cppcheck..

### Compile Commands

Next you must indicate the compile commands that are used to build your project. The `bear` command can be used to do this; it takes your build command and builds the project, recording the compile commands in a local `compile_commands.json` file.

The following command, when run in the `test` container, creates the `compile_commands.json` file for git. (Note that this file already exists, running this command would overwrite the file.)

``` sh
cd /oss/git
bear -- make
```

### Execution

Here is an example of how to run a built-in end-to-end automated code repair test, within the container (you can change the `out` directory location or directory name, but you must create that directory before running the command):

```sh
pushd /host/code/acr
mkdir test/step
python3 ./end_to_end_acr.py  /oss/git/config.c  /host/data/compile_commands.git.json  /host/data/test/sample.alerts.json    --step-dir test/step  --repaired-src test/out --base-dir /oss/git --single-file false
rm -rf test/step
```

You can see the repair using this command:

```sh
diff -u /oss/git/hash.h /host/code/acr/test/out/hash.h
```


To test a single C file that needs no fancy compile commands, you can use the "autogen" keyword instead of a `compile_commands.json` file:

```sh
pushd /host/code/acr
mkdir test/step
python3 ./end_to_end_acr.py test/test_errors.c autogen test/test_errors.alerts.json  --base-dir test --step-dir test/step --repaired-src  test/out
rm -rf test/step
```

## Extending the Redemption Tool

Documentation detail about useful environment variables and further testing is in [doc/regression_tests.md](doc/regression_tests.md). Also, a lot more detail about our system that may be of interest to others interested in extending it or just understanding it better is in the [doc](doc) directory.

## Troubleshooting

When building a Docker container, if you get an error message such as:

    error running container: from /usr/bin/crun creating container for [/bin/sh -c apt-get update]: sd-bus call: Transport endpoint is not connected: Transport endpoint is not connected : exit status 1

then try:

```sh
unset XDG_RUNTIME_DIR
unset DBUS_SESSION_BUS_ADDRESS
```

For more information, see https://github.com/containers/buildah/issues/3887#issuecomment-1085680094


## Contributions to the Redemption Codebase are Welcome

Contributions to the Redemption codebase are welcome! If you have code repairs or other contributions, we welcome that - you could submit a pull request via GitHub, or contact us if you'd prefer a different way.


