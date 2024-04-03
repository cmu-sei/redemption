# Redemption Project Simple Demo

This example demonstrates repairing a single C file with the Redemption tool

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

This is a demo scenario involving the Redemption of False Positives project.  Unless stated otherwise, any shell commands you execute should be done in this directory (`doc/examples/simple`)

## Running the Redemption Tool
### Source Code

We are using the `test_errors.c` source file (which is very similar to [this test example](../../../code/acr/test/test_errors.c).  This compiles using Clang with no warnings, but segfaults when run.  This is because it dereference null pointers on lines 11, 21, 31, and 41.

### The "good" directory

This directory contains output for each of the steps below. As you run each step, you should compare your current directory's file contents with the good directory. Assuming your step was run correctly, there will be no differences between the files that appear in both your directory and the good directory.

``` sh
diff -ru . good
```

### Static Analysis

Produce static analysis on the given C file, using Cppcheck 2.4.1.  Before generating this output, you should have the `facthunder/cppcheck:latest` Docker image downloaded.

``` sh
docker pull facthunder/cppcheck:latest
```

To generate output of the Cppcheck static analysis tool, use this command:

``` sh
docker run --rm  -v ${PWD}:/host -w /host  facthunder/cppcheck:latest  sh -c 'cppcheck -v --enable="all" --language="c" --force --xml /host/test_errors.c 2> cppcheck.xml'
```

### Convert to Redemption Input

For the rest of these instructions, you should execute the commands inside the `distrib` Docker container, and `cd` into this directory.  To set this up, use this command:

``` sh
docker run -it --rm  docker.cc.cert.org/redemption/distrib  bash
```

Then, inside the shell this command gives you:

``` sh
pushd doc/examples/simple
```

The next step is to convert the `cppcheck.xml` format into a simple JSON format that the redemption tool understands. The `alerts2input.py` file produces suitable JSON files. So you must run this script first; it will create the `alerts.json` file with the alerts you will use.

``` sh
python3 /host/code/analysis/alerts2input.py  /host  cppcheck_oss  cppcheck.xml  alerts.json
```

### Execution

Here is an example of how to run a built-in end-to-end automated code repair test, within the container (you can change the `out` directory location or directory name, but you must create that directory before running the command):

```sh
EXAMPLE=/host/doc/examples/simple
pushd /host/code/acr
python3 ./end_to_end_acr.py  ${EXAMPLE}/test_errors.c  autogen  ${EXAMPLE}/alerts.json  --repaired-src ${EXAMPLE}/out  --repair-includes false
popd
```

You can see the repairs using this command:

```sh
diff -u test_errors.c out
```
