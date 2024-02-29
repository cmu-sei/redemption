# Regression tests

This document has information about how to run the various regression tests, relevant to tests in a) the `prereq` container; b) the `test` container; and c) data and tests that you extend the system with. It also provides environment variables that may be useful for tests.

It extends information provided in the [main README.md](../README.md) about how to build the containers, run them, set environment variables, troubleshoot, and more.

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

## Summary of environment variables

```bash
export acr_show_progress=true   # Show progress and timing
export acr_warn_unlocated_alerts=true # Warn when alerts cannot be located in AST
export acr_emit_invocation=true # Show subprogram invocation information
export parser_cache=/host/code/acr/test/cache/ # Cache the output of the ear module, else set to ""
export pytest_keep=true         # Keep output of individual modules (ear, brain, etc.). Regardless, the *.nulldom.json intermediate file is kept.
export pytest_no_catch=true     # Break into debugger with "-m pdb" instead of catching exception
export REPAIR_MSC12=true     # Repair MSC12-C alerts (By default, the system DOES do the repair. The system does not do this repair if this variable is set to `false`)
```

See the [main README.md](../README.md) for information about environment variables `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS`.

## Limiting `pytest` Tests Performed

For additional info on running pytest, see the [documentation at pytest.org](https://docs.pytest.org/en/6.2.x/usage.html).

### Example with Single Test

This example shows how to use pytest with the test runner from the `/host/code/acr/test` directory of the container, to run a set of tests that should pass. This example selects the `test_two_good` test from `test_runner.py`, then output says the test passes.:

```sh
pushd /host/code/acr/test
pytest -k two_good -v
```

### Example with String-Matching Test Names

This example shows how to use pytest parameter passing to limit a test set. The command below matches test names in python test files with the string `"parameter"` in their name, which finds `test_parameter_string_matches` in `test_runner.py`. It then matches test names with the string `"simple_null"` in their name in the function-specified `.yml` file (`in.out.substrings.match.some.names.yml`). The output that prints (due to the `-s` argument in the command) specifies that three test results are compared to expected results (`count_results_compared is 3`, then `PASSED`, at output end). It compares 3 test results and passes them (two because the results exist and match, the other because both results don’t exist).

```sh
pushd /host/code/acr/test
pytest -s -k parameter --stringinput="simple_null"  -v
```

## Notes on `pytest` Results

* The pytest command results in a printout of “0 selected” if no function name matches
* The pytest command returns failure if any test fails (if the `.yml` file has one or more failures, they will each print a `FAIL` line after their test run, and then after the count of tests is printed (`count_results compared is `) there will be an overall `FAILED` output line and at the end that single `.yml` file is counted as a single failure (e.g., `1 failed`)
* The `pytest` command passes (outputs `PASSED`) if a function name matches but no string match in the .yml   (can be empty string or a different not-matching string)

## Option to Catch Exceptions or Break into Debugger

By default, the test runner catches exceptions, so that it can continue on with the next test after a failed test.  To turn off exception catching, so that you can break into the debugger when an error occurs, set the environment variable `pytest_no_catch` to `true`, e.g.:
```
export pytest_no_catch=true
cd /host/data/test
python3 -m pdb /host/code/acr/test/test_runner.py -k src_zeek_Dict_h zeek.cppcheck.EXP34-C.test.yml
```

## Test Failure Example

Next is an example pytest run with the test runner that runs 2 tests that pass, then a test that fails. So, overall the set of tests fails. With the failed assertion of success by the test runner, pytest prints details of the failing last test and prints output from the first 2 passing tests.

To run this example, **uncomment the 3 lines in `test_runner.py` starting `def test_incorrect_assertion(out_dir):`**, then run the following:

```sh
pushd /host/code/acr/test
pytest -k incorrect_assertion -v
```

After verifying that the test outputs `FAILED` as expected, re-comment the three previously-uncommented lines, so other tests again pass normally.

## Speeding up Testing by Cacheing Output of Ear Module

The ear module (which runs Clang on the codebase) usually takes a majority of the run time of the tool.  To speed things up, the output of the ear module can be cached by specifying a cache directory with the `parser_cache` environment variable:

```sh
mkdir /host/code/acr/test/cache/
export parser_cache=/host/code/acr/test/cache/
```

On one machine, this reduces the testing time from 2.8 seconds to 1.1 seconds (testing using the `pytest` command, per above).

The cached output is invalidated if the last-modification date of the corresonding `.c` file or `ear.py` is after the last-modification date of the cached-output file.  If you change another file (e.g., `util.py`) that influences the output of the ear module, make sure to manually clear the cache directory.

## `test` Docker Container

There is also a `test` Docker container that you can build and test with. It builds `git` and `zeek`. Building zeek takes about 40 minutes on one machine. Once these are built, there are some tests that test the repair tool on these codebases. To build and run the `test` container:

```sh
docker  build  -f Dockerfile.test  -t docker.cc.cert.org/redemption/test  .
docker run -it --rm -v ${PWD}:/host -w /host docker.cc.cert.org/redemption/test  bash
```

To run the tests, use the bash shell in the `test` container. The various options to speed up tests in the previous section (-k, --stringinput, etc) are useful here, too:

```sh
cd data/test
pytest
```

All tests should pass. 


Note (applies to the test container only): The above `pytest` command takes a very long time complete (e.g., over 2 hours for the 145 tests in git.rosecheckers.MSC12-C.test.yml alone) when `*MSC12-C*test.yml` files are included in the testing.
To exclude them, can move the `*MSC12-C*test.yml` files from the `data/test` directory to another location.
If you do not move them, but only set their repairs to false (`export REPAIR_MSC12=false`), testing time will still be longer than if they were moved.

## More Details about Running Tests

### `.yml` and `.json` test files

Running a test requires that a) you have a relevant `.test.yml` file for the codebase and b) at least one associated `.alerts.json` file from one of the static analysis tools. You can also have one or more `.ans` answer file(s), each specific to a particular file for the codebase that you are testing. You should have a `.ans` file for a test to pass, for the test to pass with the `.ans` file matching the test result. However, if there is no `.ans` for a test and the count of results compared is zero, then currently `test_oss` will say that `test.yml` testfile passed. This only applies to the tests in `data/test`.

### Creating `.ans` files in the test and prereq containers

For either container: If you are only going to do what we call "stumble-through" testing, the use the following command to create empty `.ans` files. ("Stumble-through" testing is just checking to see if the system errors, not validating correctness of any repairs done.) For the following command, you can (but don't need to) provide more specificity for the `test.yml` filename, e.g., `toy.*.test.yml`. 

```sh
touch `grep "answer_file" *.test.yml`
```

To make `.ans` files containing the current repair (which may be an empty file, if there's no repair), use the following instructions in either the `prereq` or `test` container:

If the `.ans` file already exists, delete it first if you want to re-create it.

Use the `--create-ans` option of `test_runner.py` to create an `.ans` file if it doesn't already exist, and you can specify tests with `-k`. e.g.:

```bash
pushd /host/data/test
python3 /host/code/acr/test/test_runner.py -k git-compat-util_h git.clang-tidy.EXP34-C.test.yml --create-ans
```

### Running tests in either container

The difference between the `prereq` and `test` containers is that the `test` container contains `git` and `zeek`. So, tests that involve repairing `git` or `zeek` must be run only in the test container. Also, the tests in `data/test` are almost only `git` and `zeek` (there are also a small set of `toy` tests).

From `/host/data/test`, run one of the following commands to test and check if this test result (diff from the original `.c` file) matches the answer if one exists. (NOTE that test commands in (a) and (c) below will provide output that counts how many comparisons with answer files were done, as well as if the test passes. However, test commands in (b) below simply state a failure or pass, and with a missing `.ans` file when there is an empty repair, there will be a pass.) :

a) Run the following command to run tests for particular `test.yml` file(s) and optionally filtering for particular test `name`(s) specified in the `test.yml` file(s)`:

`python3 test_oss.py [-k <filter>] <yml-files>`  

Example 1, in either container: `python3 test_oss.py toy.t5.test.yml`

Example 2, in the `test` container (since for `git.cppcheck.EXP34-C.test.yml`, which is for the datasets in the test container): `python3 test_oss.py git.cppcheck.EXP34-C.test.yml` or `python3 test_oss.py -k builtin_am_c git.cppcheck.EXP34-C.test.yml` 

OR

b) Run the following `pytest` command to run tests for particular `test.yml` file(s) and optionally filtering for particular `test.yml` file(s)`:

`pytest -k <filter-which-can-filter-yml-files>`

For example: `pytest -k toy.t5.test.yml`

OR

c) Run the following line of commands to run tests for all `*.test.yml` files in the directory. This tests the `toy` test files as well as those associated with `git` and `zeek`. Modify the `*.test.yml` text if you want to run tests on only a subset of the `*.test.yml` files which match a particular string (e.g., you could use `zeek.*.test.yml`).

```
for y in `ls *.test.yml`; do python3 test_oss.py $y; done
```

### `.ans` File Names

Automated tests currently automatically name the resulting intermediate and repaired files based on the input `.c` filename and NOT including the filepath. The intermediate filenames are `<filenamePrefix>.{hand,brain,ear,nulldom}-out.json` and `<filenamePrefix>.ll` which are put into the default directory (in container, `/host/code/acr/test/step`) `redemption/code/acr/test/step/` if in your container, you previously set `export pytest_keep=true`. (CAUTION: Automated tests of the same `.c` filename but different alerts and/or compile commands files will overwrite test results files from each other. JIRA issue 238 will address modifying intermediate filenames to avoid collisions.)

### Warnings for Un-located Alerts

When the redemption tool cannot match an alert to a location in the source code, the hand module has an option to print an error message `Warning: Missing ast_id for alert N`.  To turn on this message, set the environment variable `acr_warn_unlocated_alerts` to `true`.

### Showing progress

To write progress messages to stdout, set the environment variable `acr_show_progress` to `true`.

### Saving test output

If you want the test output to be saved, then prior to running the test, set the `pytest` variable to `true`, e.g., in a terminal of your container run:

`export pytest_keep=true`

After, you can change back so the test output will be removed, by running the following in a terminal of your container:

`export pytest_keep=false`


