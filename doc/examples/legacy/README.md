# Redemption Project Legacy Demo

This example demonstrates repairing a multiple-file codebase with the Redemption tool. In particular, the codebase does NOT build inside the Redemption container, but must be built inside an environment separate from the Redemption container.

The separate environment must be able to run Clang 15 (with our patch), and `bear`.

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

This is a demo scenario involving the Redemption of False Positives project.  Unless stated otherwise, any shell commands you execute should be done in this directory (`doc/examples/legacy`)

## Running the Redemption Tool
### Source Code

We are using the `wrk` codebase, version 4.2.0. It is freely available from [Github](https://github.com/wg/wrk).  For this demo, you should check it out into a subdirectory:

``` sh
cd doc/examples/legacy
git clone https://github.com/wg/wrk
cd wrk
git checkout 4.2.0
```

### The `good` directory

This directory contains output for each of the steps below. As you run each step, you should compare your current directory's file contents with the good directory. Assuming your step was run correctly, there will be no differences between the files that appear in both your directory and the good directory.

``` sh
diff -ru . good
```

If you want to skip a step (or if you are having trouble with the step), you can bypass it by copying the appropriate file from the `good` directory to the current one. For example, in the next step, you create a `compile_commands.json` file.  To skip this step simply copy the `good/compile_commands.json` file to the current directory, and use it for the subsequent steps.

You are welcome to try to repair other codebases, or other versions of the `wrk` codebase.  The following instructions have been tested by SEI, and using a different codebase, or different version of `wrk` may produce you different results than what we expect. These results will appear when you compare files you produced with files in the `good` subdirectory.

Likewise, you are welcome to use other methods than what we prescribe to produce these output files. For example, we recommend using bear 3.1.2 as contained in the Redemption container. Alternately, you could download bear from a different source or install it from source or install it using `yum` or some other package manager.  You can also produce the `compile_commands.json` file directly using Clang.  The following instructions have been tested by SEI, and using a different Cppcheck may produce different results than what we expect. These results will appear when you compare the `compile_commands.json` file you produced with then one we provided in the `good` subdirectory.

### Launching Containers

The `wrk` requires LuaJIT and OpenSSL to be installed first, which is why it will not currently build in the Redemption container.  We will therefore modify one Docker container to build `wrk` with our patched Clang, but this container will not contain Redemption. We will call this the Platform container, to distinguish it from the Redemption container.  Both container will share this `legacy` directory as a shared volume, so that they can exchange data easily.  You will therefore need two shells, one for each container.

Note that each instruction below must be run in either the Platform container or the Redemtpion container, be sure that you are executing these commands in the correct container.

#### Platform container

In one shell, you can launch the Platform container. To set this up, use these commands:

``` sh
cd doc/examples/legacy
docker  build  -f Dockerfile.legacy  -t docker.cc.cert.org/redemption/legacy  .
docker run -it --rm  -v ${PWD}:/legacy  -w /legacy  docker.cc.cert.org/redemption/legacy  bash
```

(You only have to build this container once, after that you can run it as many times as you wish.)

Note that while this container includes a basic Linux install, as well as our patched Clang, it does NOT include the Redemption code.

Inside the container, you can now build `wrk`:

``` sh
cd /legacy/wrk 
make WITH_OPENSSL=/usr WITH_LUAJIT=/usr CFLAGS="-I/usr/include/luajit-2.1 "
```

If you get an error along these lines:

``` sh
fatal: detected dubious ownership in repository at '/legacy/wrk'
To add an exception for this directory, call:

	git config --global --add safe.directory /legacy/wrk
```

Then go ahead and run the `git config` command as recommended. (This error can occur because shared files inside a container may have a different owner than the same files outside the container.)

#### Redemption container

In another shell, you can launch the Redemption container. (Do not exit the shell with the Platform container; use a separate shell). These commands launch the Redemption container:

``` sh
cd doc/examples/legacy
docker run -it --rm  -v ${PWD}:/legacy  docker.cc.cert.org/redemption/distrib  bash 
```

(See the toplevel [README.md](../../../README.md) instructions for details on how to build this container if necessary.

Then, inside the shell this command gives you:

``` sh
cd /legacy
```

You could try building `wrk` inside this container, however, you will get compilation errors, because you have not installed the necessary dependencies.

### Creating a build file (Platform container)

The following commands, when run in the `platform` container, creates the `compile_commands.json` file for wrk:

``` sh
cd /legacy/wrk
make clean
bear -- make WITH_OPENSSL=/usr WITH_LUAJIT=/usr CFLAGS="-I/usr/include/luajit-2.1 "
mv compile_commands.json  ..
```

### Static Analysis (Platform container)

Produce static analysis on the given C file, using Clang-tidy in the `platform` container.  Use this command:

``` sh
cd /legacy/wrk
clang-tidy  -checks='*'  -extra-arg=-ferror-limit=0  src/*.c  > ../clang-tidy.txt
```

The command will produce scary "Error while processing" messages. This is fine as long as the clang-tidy.txt file that is produced matches the one in the `good` directory.

### Convert to Redemption Input (Redemption container)

The next step is to convert the `clang-tidy.txt` format into a simple JSON format that the redemption tool understands. The `alerts2input.py` file produces suitable JSON files. So you must run this script first from the Redemption container; it will create the `alerts.json` file with the alerts you will use.

``` sh
cd /legacy
python3 /host/code/analysis/alerts2input.py  ${PWD}/wrk  clang_tidy_oss  clang-tidy.txt  alerts.json
```

### Execution of Redemption Phase 1 (Redemption container)

The next step is to run Phase 1, the `make_run_clang.py` script. In this phase, Redemption produces a shell script of how to run Clang on the source code.  Since Redemption cannot run Clang itself, you must run this shellscript explicitly, as the next step.

In the Redemption container, use this command:

```sh
cd /host/code/acr
python3 ./make_run_clang.py  -c /legacy/compile_commands.json  --output-clang-script /legacy/run_clang.sh
```

### Running the Clang shell script (Phase 2) (Platform container)

Next, the Clang shellscript should be run in the `platform` container. This script takes one argument: a temporary directory that contains the ASTs and .ll files generated by Clang and needed by Redemption.

```sh
cd /legacy/wrk
mkdir ../temp
/bin/sh -f /legacy/run_clang.sh /legacy/temp
```

Note that this command can be slow...it takes 90 seconds on a local SEI machine.

### Execution of Redemption (Phase 3) (Redemption container)

The final step is to run Redemption.  In this phase, Redemption repairs the source code given the Clang output from the previous shell.

```sh
cd /host/code/acr
python3 sup.py  -c /legacy/compile_commands.json  -a /legacy/alerts.json  -b /legacy/wrk  --raw-ast-dir /legacy/temp  --repaired-src /legacy/out
```

You can see the repairs using this command, in either container:

```sh
cd /legacy
diff -ru wrk out
```
