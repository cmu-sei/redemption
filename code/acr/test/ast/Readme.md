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

# AST Tests Directory

Tests for changes to clang's AST output exist here.

## scripts

| file                  | description                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------- |
| ast_comparer.py       | runs the tests provided by scenarios.json, e.g., *./ast_comparer.py --config scenarios.json*                     |
| conftest.py           |                                                                                                                  |
| json_generator.sh     | creates json files from a specified file extension, e.g., *./json_generator.sh . c*                              |
| scenario_generator.py | creates a scenarios.json file from specified file extensions, e.g., *./scenario_generator.py . c scenarios.json* |
| scenarios.json        | clang path and test details that ast_comparer.py uses                                                            |

## CMakelists.txt

for quickly testing AST traversal, you can use:

```sh
cd /host/code/acr/test/ast
mkdir build
cd build
cmake -DFILE_TO_COMPILE=../test-pointers.c ../
```

for quickly testing brainstem's parser of AST output

```sh
python3 brainstem.py /host/code/acr/test/ast/test-pointers.json -o test-pointers.out
```
