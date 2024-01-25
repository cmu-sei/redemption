# Ear Module output

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

Consider the file `assert-test.c`, whose contents are as follows:
```c
    #include <assert.h>

    int main(int argc, char** argv) {
        assert(argc > 1);
        return 0;
    }
```

When this file is run thru the C preprocessor without any options, the `assert(argc > 1)` line becomes:

```c
   ((void) sizeof ((
   argc > 1
   ) ? 1 : 0), __extension__ ({ if (
   argc > 1
   ) ; else __assert_fail (
   "argc > 1"
   , "assert-test.c", 4, __extension__ __PRETTY_FUNCTION__); }))
```

But with the `-DNDEBUG` option, the line becomes:

```c
   ((void) (0))
```

The ear output contains the ASTs of the above preprocessed code.  For example, you can get the ear output as follows:

```bash
    cd /host/code/acr/test
    ../ear.py -o out/assert-test.ear-out.json        -s assert-test.c -c autogen
    ../ear.py -o out/assert-test.ear-out.NDEBUG.json -s assert-test.c -c assert-test.compile_cmds.NDEBUG.json
```

where `assert-test.compile_cmds.NDEBUG.json` specifies the `-DNDEBUG` argument.

So, to check whether an `assert` in a given translation unit is disabled, you can grep for `__assert_fail` in the ear output.  With `test_runner.py`, the ear output goes in the step directory (default: `/host/code/acr/test/step`), provided that `pytest_keep` is `true`.
