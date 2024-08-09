# Redemption Project Separate-Build Demo

This example demonstrates how to use the Redemption automated code repair tool with a separate code build environment (code build environment outside the Redemption Docker container)
how to repair a codebase with the Redemption tool, with the specific constraint that the codebase does NOT build inside the Redemption container, but can only be built in an environment distinct from the Redemption container.

To accomplish this demo, we will create two containers, which we call the Build Platform and Repair Platform. The Repair Platform is simply the Redemption container, which can repair code, but it will not be able to build the code that we are repairing.  (That is, trying to build the code in the Repair Platform will generate errors.)  The Build Platform will be a platform that is suitable for building a codebase, but it will not run Redemption code.  Each platform will support one shell for receiving commands.

The Build Platform must be able to run Clang 15 (with our patch), and the `bear` utility. Using `bear` requires the code to be compilable using a single command, which could use a Makefile, a script, or various other options.  See the [I Cannot Install Bear](#i-cannot-install-bear) section if you can not install `bear`.

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

<a name="clang-15-on-the-build-platform"></a>
## Clang 15 on the Build Platform

The Redemption tool provides a modification to Clang for producing additional information that is needed by the rest of the Redemption tool.  The modification is in the form of several C++ files that built as part of clang, but we have extended them; our modifications currently live [here](../../../code/clang).  The Redemption Docker container already has the modified Clang built, but if you wish to use Clang outside the Redemption container as this document demonstrates, then additional steps are needed to build Clang with these Redemption patches on your platform.

For this demo, you can use the Build Platform container described below in the [Build Platform](#build-platform) section, which already has Clang built with our modifications.  But when you want to run Redemption on code that builds on some platform, but not in the Redemption Container, you must make that platform your Build Platform. That is, you must install Clang 15 with the Redemption modifications on your own build platform.

While you could install Clang 15 binaries on your platform, the Redemption enhancements require Clang 15 to be compiled from source on your platform. The Clang 15 source can be downloaded from [Clang's Github repository](https://github.com/llvm/llvm-project/releases/tag/llvmorg-15.0.7).

To apply the patch and build Clang, you must first install necessary dependencies. Details about necessary dependencies are available at [LLVM's website](https://llvm.org/docs/GettingStarted.html#requirements).  You must then copy several files from the `code/clang` directory into the Clang source before building.

The [`Dockerfile.prereq`](../../../Dockerfile.prereq) file contains precise shell commands for downloading, preparing, and building Clang on a container running Ubuntu Linux 24.04 ("Noble Numbat").  The dependencies begin on the first line that says "Apt packages". The line that says `modified clang based on 15.0.7` concludes dependencies, and begins the process of downloading, preparing, and building Clang, and these commands end at the line that says `clang is built in /opt/clang/build/bin`.

If you are using a different OS, the precise commands that you should use will depend on your OS.

The commands to download, prepare, and build Clang (from the `Dockerfile.prereq` file) are as follows...they should be executed from the top directory (the same directory that contains `Dockerfile.prereq`):

```sh
mkdir /opt/clang
git clone  --depth=1  --branch llvmorg-15.0.7  https://github.com/llvm/llvm-project.git  /opt/clang

cp  code/clang/*.h  /opt/clang/clang/include/clang/AST
cp  code/clang/*.cpp  /opt/clang/clang/lib/AST

mkdir /opt/clang/build
cmake -G Ninja -S/opt/clang/llvm -B/opt/clang/build -DLLVM_ENABLE_PROJECTS="clang" -DLLVM_USE_LINKER=lld -DLLVM_BUILD_TESTS=OFF -DLLVM_TARGETS_TO_BUILD="X86" -DLLVM_BUILD_EXAMPLES=OFF -DLLVM_INCLUDE_EXAMPLES=OFF -DLLVM_LIBDIR_SUFFIX=64 -DCMAKE_BUILD_TYPE=Release
ninja -C /opt/clang/build
```

The build make take several hours, depending on your platform's speed.

## Running the Redemption Tool
### Source Code

We will repair the `wrk` codebase, version 4.2.0. It is freely available from [Github](https://github.com/wg/wrk).  For this demo, you should check it out into a subdirectory:

``` sh
cd doc/examples/separate_build
git clone https://github.com/wg/wrk
cd wrk
git checkout 4.2.0
```

### The `good` directory

This directory contains output for each of the steps below. As you run each step, you should compare your current directory's file contents with the good directory. Assuming your step was run correctly, there will be no differences between the files that appear in both your directory and the good directory.  There will be files in the good directory that do not appear in the current directory. But every file that appears in both directories should be identical.

``` sh
cd doc/examples/separate_build
diff -ru . good
```

If you want to skip a step (or if you are having trouble with the step), you can bypass it by copying the appropriate file from the `good` directory to the current one. For example, in the next step, you create a `compile_commands.json` file.  To skip this step simply copy the `good/compile_commands.json` file to the current directory, and use it for the subsequent steps.

You are welcome to try to repair other codebases, or other versions of the `wrk` codebase.  The following instructions have been tested by SEI, and using a different codebase, or different version of `wrk` may produce you different results than what we expect. These results will appear when you compare files you produced with files in the `good` subdirectory.

Likewise, you are welcome to use other methods than what we prescribe to produce these output files. For example, we recommend using bear 3.1.2 as contained in the Repair Platform. Alternately, you could download bear from a different source or install it from source or install it using `yum` or some other package manager.  You can also produce the `compile_commands.json` file directly using Clang.  The following instructions have been tested by SEI, and using a different Cppcheck may produce different results than what we expect. These results will appear when you compare the `compile_commands.json` file you produced with then one we provided in the `good` subdirectory.

### Launching Containers

The `wrk` requires LuaJIT and OpenSSL to be installed first, which is why it will not currently build in the Repair Platform (which is the same as the redemption container).  We will therefore create a Docker container to build `wrk` with our patched Clang, but this container will not contain the Redemption code.  This will be our Build Platform, to distinguish it from the Repair Platform.  Both platforms (that is, containers) will share this `separate_build` directory as a shared volume, so that they can exchange data easily.  You will therefore need two shells, one for each container.

If you have a separate host or container that contains Clang 15 with the enhancements from Redemption in it, you may use that as your Build Platform. See the [Clang 15 on the Build Platform](#clang-15-on-the-build-platform) section for details about setting up an appropriate Build Platform.

Note that each instruction below must be run in either the Build Platform or the Repair Platform, be sure that you are executing these commands in the correct platform.

<a name="build-platform"></a>
#### Build Platform

In one shell, you can launch the Build Platform. To set this up, use these commands:

``` sh
cd doc/examples/separate_build
docker  build  -f Dockerfile.separate_build  -t ghcr.io/cmu-sei/redemption-separate_build  .
docker run -it --rm  -v ${PWD}:/separate_build  -w /separate_build  ghcr.io/cmu-sei/redemption-separate_build  bash
```

(You only have to build this container once, after that you can run it as many times as you wish.)

Note that while this container includes a basic Linux install, as well as our patched Clang, it does NOT include the Redemption code.

Inside the container, you can now build `wrk`:

``` sh
cd /separate_build/wrk
make WITH_OPENSSL=/usr WITH_LUAJIT=/usr CFLAGS="-I/usr/include/luajit-2.1 "
```

See the [Troubleshooting](#troubleshooting) section if you get any errors.

#### Repair Platform

In another shell, you can launch the Repair Platform. (Do not exit the shell with the Build Platform; use a separate shell). These commands launch the Repair Platform:

``` sh
cd doc/examples/separate_build
docker run -it --rm  -v ${PWD}:/separate_build  ghcr.io/cmu-sei/redemption-distrib  bash 
```

(See the toplevel [README.md](../../../README.md) instructions for details on how to build this container if necessary.

(You could try building `wrk` inside this container, however, you will get compilation errors, because you have not installed the necessary dependencies.)

<a name="creating-a-build-file"></a>
### Creating a Build File (Build Platform)

The following commands, when run in the Build Platform, creates the `compile_commands.json` file for wrk:

``` sh
cd /separate_build/wrk
make clean
bear -- make WITH_OPENSSL=/usr WITH_LUAJIT=/usr CFLAGS="-I/usr/include/luajit-2.1 "
mv compile_commands.json  ..
```

See the [I Cannot Install Bear](#i-cannot-install-bear) section if you can not install `bear`.

### Static Analysis (Build Platform)

Produce static analysis on the given C file, using Clang-tidy in the Build Platform.  Use this command:

``` sh
cd /separate_build/wrk
grep --color=none '"file":' ../compile_commands.json | sed 's/"file"://;  s/",/"/;' | sort -u  | xargs clang-tidy-16 -checks='*'  > ../clang-tidy.txt
```

### Convert to Redemption Input (Repair Platform)

The next step is to convert the `clang-tidy.txt` format into a simple JSON format that the redemption tool understands. The `alerts2input.py` file produces suitable JSON files. So you must run this script first from the Repair Platform; it will create the `alerts.json` file with the alerts you will use.

This step requires the `clang-tidy.txt` file produced in the Build Platform from the previous step.

``` sh
cd /separate_build
python3 /host/code/analysis/alerts2input.py  ${PWD}/wrk  clang_tidy  clang-tidy.txt  alerts.json
```

### Execution of Redemption Phase 1 (Repair Platform)

The next step is to run Phase 1, the `make_run_clang.py` script. In this phase, Redemption produces a shell script of how to run Clang on the source code.  Since Redemption cannot run Clang itself, you must run this shellscript explicitly, as the next step.

This step requires the `compile_commands.json` file produced in the Build Platform from the [Creating a Build File](#creating-a-build-file) step.

In the Repair Platform, use this command:

```sh
cd /host/code/acr
python3 ./make_run_clang.py  -c /separate_build/compile_commands.json  --output-clang-script /separate_build/run_clang.sh
```

### Running the Clang shell script (Phase 2) (Build Platform)

Next, the Clang shellscript should be run in the Build Platform. This script takes one argument: a temporary directory that contains the ASTs and .ll files generated by Clang and needed by Redemption.

This step requires the `run_clang.sh` file produced in the Repair Platform from the previous step.

```sh
cd /separate_build/wrk
mkdir ../temp
/bin/sh -f /separate_build/run_clang.sh /separate_build/temp
```

Note that this command can be slow...it takes 90 seconds on a local SEI machine.

### Execution of Redemption (Phase 3) (Repair Platform)

The final step is to run Redemption.  In this phase, Redemption repairs the source code given the Clang output from the previous shell.

This step requires all of the `.ast.json.gz` and `.ll` files from the `temp` directory that were produced in the Build Platform from the previous step. This step also requires the `compile_commands.json` file produced in the Build Platform from the [Creating a Build File](#creating-a-build-file) step. On one of our test machines, this resulted in a wait of around 3 minutes prior to getting output from the command.

```sh
cd /host/code/acr
python3 sup.py  -c /separate_build/compile_commands.json  -a /separate_build/alerts.json  -b /separate_build/wrk  --raw-ast-dir /separate_build/temp  --repaired-src /separate_build/out
cd /separate_build
diff -ru --label=ORIGINAL --label=REPAIRED -ru  wrk  out > repaired.diffs 
```

The `repaired.diffs` file contains all the specific repairs made to the code.

<a name="troubleshooting"></a>
## Troubleshooting

If you get an error along these lines when trying to build `wrk`:

``` sh
fatal: detected dubious ownership in repository at '/separate_build/wrk'
To add an exception for this directory, call:

	git config --global --add safe.directory /separate_build/wrk
```

Then go ahead and run the `git config` command as recommended. (This error can occur because shared files inside one Docker container may have a different owner than the same files outside the container.)

<a name="i-cannot-install-bear"></a>
### I cannot install `bear`

The `bear` command is useful for building compilation databases, aka the `compile_commands.json` file, which is used by Redemption to understand how software is built. For more info on `bear`, see: https://github.com/rizsotto/Bear ).

If you cannot install or run Bear on the build platform, you must create the compilation database via other means. The [format of the JSON compilation database](https://clang.llvm.org/docs/JSONCompilationDatabase.html) contains a specification of the compilation database.  It also contains instructions for producing this database using Clang.  The format is fairly straightforward, and so you might be able to produce the file manually.
