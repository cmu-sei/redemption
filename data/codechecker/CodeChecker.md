---
title: CodeChecker'
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

CodeChecker
==================

Introduction
------------

CodeChecker is an open-source static-analysis tool framework. It
permits the execution of several other SA tools. By default it runs
Clang-tidy and the clang-static-analyzer, but you can also add
cppcheck, and several other SA tools.  It is open-source software
available under a [permissive license](https://github.com/Ericsson/codechecker/blob/master/LICENSE.TXT){.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png).
You can read more about CodeChecker at its project page:
<https://codechecker.readthedocs.io/en/latest/>{.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png)

CodeChecker can be run from the command-line. While CodeChecker
provides a server for storing and managing alerts produced by the SA
tools it manages, it also can export them in several formats.

Running a Scan
--------------

### Command Line

You will want to create a `compile_commands.json` file, and the easiest
way to do this is to use the `bear` command with your build process.
If your project is built using a `make build` command, then you can
do:

```sh
bear make build
```

CodeChecker can also do this with a similar command:

```sh
CodeChecker log --build "make build" --output ./compile_commands.json
```

To analyze source files with all the CERT-related checkers:

```sh
CodeChecker analyze --enable-all ./compile_commands.json  --output reports.codechecker 
```

Once this is done, you can export the alerts to JSON:

```sh
CodeChecker parse -e json reports.codechecker | python3 -m json.tool > codechecker.json
```
