---
title: Clang'
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

Clang
==============

Introduction
------------

Clang is a C/C++ compiler that uses the LLVM framework for
optimization. It includes a static analysis tool (called
`build-scan`. It is open-source software available under a [permissive
license](https://opensource.org/licenses/NCSA){.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png).
You can read more about Clang at its project page:
<https://clang-analyzer.llvm.org/>{.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png)

Clang scans can be run from the command-line. It can produce output in the form of Apple-style property lists `.plist` or HTML pages (or both).

Once you have the ZIP output, here are instructions for [Converting Text Output to ORG files](Back-End-Script-Design.md#properties).

Running a Scan
--------------

### Command Line

Suppose we want to scan some C sources located under the directory
`/home/user/project` and want to save the results to a file named
`results.zip`. Also, suppose the project has a Makefile, so it can be
built with the command `make`. From the command-line (Ubuntu), we can
run the following:

```sh
scan-build -plist -o /home/user/clang.out    make
```
or, if you also want HTML output, that you can examine in your browser:
```sh
scan-build -plist-html -o /home/user/clang.out    make
```

All that remains is to bundle the output into a ZIP file.
```sh
cd /home/user/clang.out
zip -r clang.out.zip  *
```
