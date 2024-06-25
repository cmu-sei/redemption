# Redemption Project Simple Demo

This example demonstrates repairing a single C file with the Redemption tool

Unless stated otherwise, any shell commands you execute should be done in this directory (`doc/examples/simple`)

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

## Running the Redemption Tool
### Source Code

We are using the `test_errors.c` source file (which is very similar to [this test example](../../../code/acr/test/test_errors.c).  This compiles using Clang with no warnings, but segfaults when run.  This is because it dereference null pointers on lines 11, 21, 31, and 41.

### The "good" directory

This directory contains output for each of the steps below. As you run each step, you should compare your current directory's file contents with the good directory. Assuming your step was run correctly, there will be no differences between the files that appear in both your directory and the good directory.

``` sh
cd doc/examples/simple
diff -ru . good
```

If you want to skip a step (or if you are having trouble with the step), you can bypass it by copying the appropriate file from the `good` directory to the current one. For example, in the next step, you create a `cppcheck.xml` file.  To skip this step, copy the `good/cppcheck.xml` file to the current directory, and use it for the subsequent steps.

You can try to use other methods than what we prescribe to produce these output files. For example, we recommend using Cppcheck 2.4.1 as contained in the `facthunder/cppcheck:latest` Docker container. Alternately, you could download Cppcheck from Github, or compile it from source or install it using `yum` or some other package manager.  You can also experiment with different (or newer) versions of Cppcheck.  The instructions we provide have been tested by SEI.  Using a different version of Cppcheck may generate different alerts than what we expect, or a different version of Cppcheck may output a different format of alert, that our parser does not expect.  You will encounter any such problems when you compare the `cppcheck.xml` file you produced with the one provided in the `good` subdirectory.

### Static Analysis

Produce static analysis on the given C file, using Cppcheck 2.4.1.  Before generating this output, you should have the `facthunder/cppcheck:latest` Docker image downloaded.

``` sh
docker pull facthunder/cppcheck:latest
```

To generate output of the Cppcheck static analysis tool, go into the directory containing this README file (`doc/examples/simple`), and use this command:

``` sh
docker run --rm  -v ${PWD}:/code -w /code  facthunder/cppcheck:latest  sh -c 'cppcheck -v --enable="all" --language="c" --force --xml /code/test_errors.c 2> cppcheck.xml'
```

### Convert to Redemption Input

For the rest of these instructions, you should execute the commands inside the `distrib` Docker container, and `cd` into this directory. 

To set this up, go to the base Redemption directory and run the Docker container, using these commands:

``` sh
cd ../../..
docker run -it --rm  -v ${PWD}:/code  docker.cc.cert.org/redemption/distrib  bash
```

(See the toplevel [README.md](../../../README.md) instructions for details on how to build this container if necessary.

Then, inside the shell this command gives you:

``` sh
pushd doc/examples/simple
cp /code/doc/examples/simple/cppcheck.xml .
```

The next step is to convert the `cppcheck.xml` format into a simple JSON format that the redemption tool understands. The `alerts2input.py` file produces suitable JSON files. So you must run this script first; it will create the `alerts.json` file with the alerts you will use.

``` sh
python3 /host/code/analysis/alerts2input.py  /code  cppcheck_oss  cppcheck.xml  alerts.json
```

### Execution

Here is an example of how to run a built-in end-to-end automated code repair test, within the container (you can change the `out` directory location or directory name, but you must create that directory before running the command):

```sh
#[NOTES] This example is wrong "--alerts" does not work with end_to_end_acr.py
EXAMPLE=/host/doc/examples/simple
pushd /host/code/acr
python3 ./end_to_end_acr.py  ${EXAMPLE}/test_errors.c  autogen  --alerts ${EXAMPLE}/alerts.json  --repaired-src ${EXAMPLE}/out
popd
```

You can see the repairs using this command:

```sh
diff -u test_errors.c out
```
