# Scripts Supporting Sample Alert Experiments
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

## Scripts that support sample alert experiments and related testing

We provide scripts that can be used to run tests and process results for sample testing experiments and related testing.
Details including script location, what the scripts do, and how to run them are provided
in this document.

### General steps for running sample alert experiment tests

Steps needed to run these tests are listed directly below. The scripts info in the sections below that show that some of these steps have been automated:

1.	Create empty .ans files for the adjudicated alerts that don’t yet have them
2.	Set environmental variables so that brain output will be saved in step directory, if you want to inspect or use that
3.	Delete extra output files that you don’t need anymore, from step directory while doing step 4 (repeatedly, so you don't run out of disk space)
4.	Run tests AND create (full if they are supposed to create anything!) .ans files (preferably of only the adjudicated alerts) using `-e` argument so that test.yml.alert_info.json files get created with specific brain output 
5.	Delete .ans files for alerts where all alerts are unsatisfactory (save backup, for possible re-adding after state-counting steps later)
6.	Careful to delete extra files don’t need from step directory (repeatedly) while doing step 4 
7.	Check if there are any wrong-state results. If yes, make adjudication changes. The `test_satisfaction_status_tables.py` output says what changes to make, for several of the wrong-state results.
8.	Repeat steps 4-7 until no more remaining
9.	Gather data using data/test/test_satisfaction_status_table.py  and if you are an SEI person, enter it on the SEI wiki page 
10.	Make JIRA issues for the unsatisfactory alerts, if you are an SEI person.




### 1. `loop_test_oss.sh`

`data/test/loop_test_oss.sh`: runs tests for all current OSS permutations of rule/tool/codebase using full `test.yml` files and creates `alerts_info.json` files

Run this script in directory redemption.public/data/test
with no arguments. It will run tests using the test data, and will 
create files with additional info about alerts.

Benefits: It runs lots of tests run producing `alerts_info.json` files, you don't need to do anything manual after starting the script except (after this script finishes), running the very-fast `test_satisfaction_status_table.py` to get all the sample alert experiment results summaries.

Drawbacks: Takes a long time to run, since it processes all tests. Also, can use far too much disk space for intermediate files.

CAUTION: if you are saving intermediate files, be careful running this as-is. The zeek files
take a lot of disk space and you might run out of disk space. 
If you are worried about running out of space, you may prefer to:

1. modify the loops to run fewer combinations (e.g., only `cppcheck` and `EXP33-C`); OR

2. you may prefer to only test the adjudicated alerts (see `adjudicated_alerts_info_and_repair.py`, below).

### 2. `test_satisfaction_status_table.py`

`data/test/test_satisfaction_status_table.py`: This is for step 7; run this to summarize states per alert and across sets of tests (output with a bit of detail at top, then summary at end after "****" line, with output that can be copied to wiki page)

This script gathers info about which state adjudicated alerts result in, A-G (or none of those, if its adjudication
combined with Redemption tool processing results in an incorrect state).
The script gathers alert totals per-state and satisfaction ratio data, for each of the
OSS test permutations of {codebase, tool, rule} in our OSS test dataset.
The ending data after the "****" line can be copy/pasted into SEI's internal "experiments and other testing"
wiki page's "sample testing" table.

Prerequisites: Tests should have previously been run with `-e`, resulting in ".test.yml.alerts_info.json" files. See comments at the top of the script, about prerequisites for environment variables.

Detail on running: Run this script in directory `redemption.public/data/test` with no arguments.

Benefit: Fast to run. Provides summary at end of output with the per-testfile test satisfaction counts and ratios, plus unmatched states and errors. You can copy the count and ratio data and paste it to the SEI sample testing table. It provides more detail, including about unmatched states and errors, in the top part of the output.


### 3. `adjudicated_alerts_info_and_repair.py`

`data/test/adjudicated_alerts_info_and_repair.py` : runs tests on the adjudicated alerts in one alerts.json file, with assumptions as specified (not necessarily all adjudicated alerts in that file, only the set identified for sample testing)

This script runs tests on adjudicated alerts from a single alerts.json file and gathers data about their repair in `*out.txt` file, `*brain-out.json`, and `*.diff` files (latter 2 put in new subdirectory under `step` directory). Prerequisites include setting environment variables per the comments at the top of the file. It assumes related alerts.json and test.yml files have the same prefix. It puts the brain output and .diff files into a subdirectory of the step directory. It 1. identifies adjudicated alerts; 2. identifies the associated test name; and also (with the -t argument) 3. checks if a .ans file currently exists and creates one if it does not (using test_runner.py); 4. runs the test which compares against the .ans file; 5. redirects output from testing to a .txt file; and 6. deletes a bunch of large files in the step directory.  After this step, manually we can inspect the output file contents, and compare those to the adjudication and current "satisfactory" entry if any, and may edit the "satisfactory" value (e.g., it may become `true` after a repair has been implemented). In the future, would be nice to combine this with step 7 automated creation of summary for each adjudicated alert: test name, if .ans previously existed, if .ans was created, and result of test (pass/fail), latter with some functionality in `test_satisfaction_status_table.py`

Benefit: This script is relatively fast to run since it only runs tests on adjudicated alerts identified for sample testing from a single alerts.json file. Limited disk space is required for intermediate results, due to the limited number of tests run. Testers can manually inspect output to update state counts and ratios or else to fix errors (e.g., if a result doesn't match state A-G).

Possible drawback: Even the limited disk space used by this script might be too large compared to available space, so users should inspect their system first to ensure adequate disk space.

### 4. `create-ans-files-2.py`

`data/test/create-ans-files-2.py` Helps with step 1. The script identifies adjudicated alerts, and create .ans files if they don’t already exist for only adjudicated “satisfactory” alerts (or just prints -ans filenames for the “satisfactory” set.) To run: Before running, set env variables as in comments at top. Then, provide single alerts.json filename. 1. Use -t to actually run tests AND create .ans files IF they don’t already exist; 2. Use -v (verbose) just to find out which .ans filenames are in the “satisfactory” list.


### 5. `test_runner.py`

`code/acr/test/test_runner.py`: This script has been enhanced so now it gathers, stores, and process the additional data needed for identifying states A-G. Run it with argument `-e` for that info to be gathered.

Benefit (if running it separate from the above scripts): You can run it on a single test, using arguments `-k` and the individual test name and argument `-e` so the patch and `is_fp` information from the `brain-out.json` data are gathered. (You can also run it with the `--create-ans` argument so it creates a .ans file for the test if there wasn't one already. `.ans` files for failing tests should be deleted after use, so regression etc. tests have expected results and don't bother to retest known-failing tests.) That makes it fast to run and uses minimal hard drive space. (Still, before running it, you should ensure you have disk space for intermediate files you will create.) You can then manually check the results to manually identify the state (and any error or unmatched state, and fix such a result). For SEI users, then they  can update the SEI wiki page's sample testing table.

## Future work

In the future, it would be helpful to do the following to build on the above capabilities:

* combine scripts so less needs to be done manually
* consider possibly automating edits to alerts.json adjudications when results from `test_satisfaction_status_table.py` indicates the change is required
* modify scripts so they take arguments instead of hardcoding so much