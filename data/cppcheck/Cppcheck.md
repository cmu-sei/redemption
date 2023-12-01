---
title: Cppcheck'
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

Cppcheck
=================

Introduction
------------

Cppcheck is a static analysis tool for C and C++. It is free software
available under the GNU GPL. You can read more about Cppcheck at their
Sourceforge page:<http://cppcheck.sourceforge.net/>{.extlink}![(lightbulb)](images/icons/emoticons/lightbulb_on.png)

Cppcheck scans can be run via a GUI or on the command-line. We'll be
outputting scan results as XML.

Running a Scan
--------------

### Command Line

Suppose we want to scan some C sources located under the directory
`/home/user/project` and want to save the results to a file named
`results.xml`.  From the command-line (Ubuntu), we can run the
following:

``` sh
cppcheck --enable="all" --language="c" --force --xml ${PWD} 2> results.xml
```

If you have a compile_commands.json file, you can do:

``` sh
cppcheck --enable="all" --force --xml  --project=compile_commands.json  2> cppcheck_bear.xml
```

We enable all checkers (`--enable="all"`), indicate that the target
language is C (`--language="c"`), and output results as XML
(`--xml`). The XML is sent to `stderr`, so we redirect `stderr` to
capture this output.

The `--force` option forces cppcheck to go arbitrarily deep into
#ifdef nesting...without this option, cppcheck will only nest 12
levels deep.

On Windows, the command is very similar:

```sh
cd "C:\Program Files\Cppcheck" .\cppcheck.exe --enable="all" --language="c" --force --xml C:\MyProject 2> C:\myfolder\results.xml
```

If you are scanning a C++ project, you can change the `--language`
parameter to `--language="c++"`.  If you want to run checkers for both
languages, you can exclude the language parameter.

### GUI

Cppcheck has a graphical user interface (GUI) for Windows machines.
After installing Cppcheck on your Windows machine, open the Cppcheck
application. Click on the icon in the top left corner, and select the
directory you want to scan. The scan will start immediately.

![](attachments/cppcheck.png)

When the scan is finished, export the results to XML by navigating to
the menu "File-&gt;Save Results to File".  Decide where to save your
results and ensure "Save as type" is set to "XML files version 1
(\*.xml)".  Click Save to generate the XML file:

![](attachments/SaveAs.png)
