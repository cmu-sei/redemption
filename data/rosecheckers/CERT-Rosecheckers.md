---
title: CERT Rosecheckers'
---
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

CERT Rosecheckers
=========================

CERT Rosecheckers is an open-source static analysis tool. It was developed by
the CERT Division to look for violations of the CERT C Coding Standard.

The `rosecheckers` command takes the same arguments as the GCC compiler,
but instead of compiling the code, CERT Rosecheckers prints alerts. To
run CERT Rosecheckers on a single file, pass rosecheckers the same arguments
that you would pass to GCC. You do not have to explicitly specify
warnings to GCC like you do when harvesting its output, as
specified [here](GCC-Warnings.md). To run CERT Rosecheckers on a
codebase with multiple source files, use either of the following two
approaches.

### Substitution

In this approach, you replace GCC with a program that both runs GCC
and your static-analysis tool (rosecheckers, in this case), using the
`my-gcc.sh` script. It runs both
`gcc`
and `rosecheckers` with
the arguments given to it.

There are several approaches to using `my-gcc.sh`:

First, if your build system lets you override the compiler, you simply
execute the build system setting the compiler to `my-gcc.sh`:

    ```
    make CC=/host/code/analysis/my-gcc.sh all
    ```

If you are using the C++ compiler, your command would be:

    ```
    make CCC=/host/code/analysis/my-gcc.sh all
    ```

and you would want to tweak `my-gcc.sh` to call `g++` instead of `gcc`.

A different approach is to fool the build system without telling it that it is not directly calling `gcc`. To do this:

-   Rename this script to
    `gcc` and ensure it is in your
    `$PATH`, so when
    your build system invokes `gcc`, it really invokes `my-gcc.sh` instead.
-   Make the renamed-script files executable (`chmod 700`)
-   You must modify the line with the `rosecheckers` command, to provide
    the correct path on your own machine. (As of 7/12/18, currently it
    references a path `/home/rose/src/rosecheckers/rosecheckers`)
-   Then perform a normal build, and redirect the raw output into a text
    file.
