---
title: Clang-tidy'
---
<legal>  
'Redemption' Automated Code Repair Tool  
  
Copyright 2023 Carnegie Mellon University.  
  
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

Clang-tidy
==================

Introduction
------------

Clang-tidy is the static-analyhsis tool associated with Clang. Clang
is a C/C++ compiler that uses the LLVM framework for optimization.  It
is open-source software available under a [permissive
license](https://opensource.org/licenses/NCSA){.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png).  You can read more about Clang
at its project page:
<https://clang-analyzer.llvm.org/>{.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png)

Clang-tidy can be run from the command-line. It can produce output in
the format similar to compiler error messages...These should be piped
to a file.

Running a Scan
--------------

### Command Line

You will want to create a `compile_commandsproject.json` file, and the easiest
way to do this is to use the `bear` command with your build process.
If your project is built using a `make build` command, then you can
do:

```sh
bear make build
```

You must then procure all the source files. This could be done with a
grep command and some judicious text editing:

```sh
grep '"file"' compile_commands.json
```

Once this is done, you can run clang-tidy on the sources:

```sh
clang-tidy -checks='*' ${SOURCE} > clang-tidy.txt
```

Note that clang-tidy will reference the compile_commands.json file for compilation details if the file exists, even if you don't specify it on the command line. So you will get better results if you create it before running clang-tidy.
