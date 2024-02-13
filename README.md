# Redemption project

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

This is the Redemption of False Positives project.

There are some useful commands below for working with this code.

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

## Testing the Redemption Tool

The tool has a simple sanity test that you can run in the 'prereq' container. To run these tests:

```sh
cd code/acr/test
pytest
```

All tests should pass.

There is also a 'test' Docker container that you can build and test with. It builds `git` and `zeek`. Building zeek takes about 40 minutes on my machine. Once these are built, there are some tests that test the repair tool on these codebases.

To build and run the 'test' container:

```sh
docker  build  -f Dockerfile.test  -t docker.cc.cert.org/redemption/test  .
docker run -it --rm -v ${PWD}:/host -w /host docker.cc.cert.org/redemption/test  bash
```

To run the tests, use the bash shell in the 'test' container:

```sh
cd data/test
pytest
```

Again, all tests should pass.

## Running the Redemption Tool

For a simple demo of running the tool, see the [simple example](doc/examples/simple/README.md).

### Static Analysis

The Redemption Tool presumes that you have static-analysis tool output.  It currently supports three SA tools:  `clang_tidy_oss` or `cppcheck_oss` or `rosecheckers_oss`. Each SA tool should produce a file with the alerts it generated. If `$TOOL` represents your tool, instructions for generating the alerts file live in `data/$TOOL/$TOOL.md`.  We will assume you have run the tool, and created the alerts file, which we will call `alerts.txt`. (The actual file need not be a text file).  Finally, when you produced your SA output, the code you ran was in a directory which we'll call the `$BASE_DIR`.

### Convert to Input

Next, you must convert the `alerts.txt` format into a simple JSON format that the redemption tool understands. The `alerts2input.py` file produces suitable JSON files. So you must run this script first; it will create the `alerts.json` file with the alerts you will use.

``` sh
python3 /host/code/analysis/alerts2input.py  $BASE_DIR  clang_tidy_oss  alerts.txt  alerts.json
```

For example, the 'test' Docker container contains the source code for Git, as well as Cppcheck output.  So you can convert Cppcheck's output to alerts using this script:

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

The following command, when run in the 'test' container, creates the `compile_commands.json` file for git. (Note that this file already exists, running this command would overwrite the file.)

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

### Troubleshooting

When building a Docker container, if you get an error message such as:

    error running container: from /usr/bin/crun creating container for [/bin/sh -c apt-get update]: sd-bus call: Transport endpoint is not connected: Transport endpoint is not connected : exit status 1

then try:

```sh
unset XDG_RUNTIME_DIR
unset DBUS_SESSION_BUS_ADDRESS
```

For more information, see https://github.com/containers/buildah/issues/3887#issuecomment-1085680094

### Summary of environment variables

```bash
export pytest_keep=true         # Keep output of individual modules (ear, brain, etc.)
export parser_cache=/host/code/acr/test/cache/ # Cache the output of the ear module
export acr_show_progress=true   # Show progress and timing
export acr_warn_unlocated_alerts=true # Warn when alerts cannot be located in AST
export pytest_no_catch=true     # Break into debugger with "-m pdb" instead of catching exception
```

### Measuring and Improving Satisfactory Alert Redemption

One of our measures of satisfactory alert redemption is done by randomly selecting alerts to manually adjudicate (using web-based random number generators and the number of alerts in the output), manually adjudicating and analyzing if automated repair should be done, then inspecting if our tool automatically and correctly repairs them. Scripts like `data/test/adjudicated_alerts_info_and_repair.py` and `data/test/test_satisfaction_status_tables.sh` help automate the process of running tests on the adjudicated alerts and then gathering overall statistics on satisfactorily handling the adjudicated alerts into tables. The latter table-creating script specifies particular datasets, coding rules, and static analysis tools but those lists can be easily extended or substituted. You can use the scripts to measure satisfactory alert redemption on your own codebases, tools, and code flaw taxonomy items of interest. Results can be used to target efforts to integrate particular code repairs, e.g., if those would eliminate many alerts and/or alerts with code flaws of particular interest. Contributions to the Redemption codebase are welcome! If you have code repairs or other contributions, we welcome that - you could submit a pull request via GitHub, or contact us if you'd prefer a different way.