# How to Test the Automated Code Repair (ACR) tool

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

## Component Testing

We are using Pytest to test the various components.

## OSS Tests

To test the entire ACR tool, we have produced alerts using these SA tools:
 * cppcheck
 * clang-tidy
 * rosecheckers
The alerts are for the first three CERT guidelines we repair, which are:
 * EXP34-C (null-pointer dereferences)
 * EXP33-C (uninitialized values)
 * MSC12-C (dead code)
The alerts were produced by running SA tools over the following OSS codebases:
 * git
 * zeek

## Sample Alert Testing

In this scenario, we pick a single C file that has 1 or more alerts that we wish to repair. We have ACR repair the alerts, and then compare the repaired source code against an 'answer' source code file. The test passes if the test result matches the answer file.

The following two tables indicates how many alerts were generated:

| git          | EXP34-C | EXP33-C | MSC12-C |
|--------------|---------|---------|---------|
| cppcheck     |      20 |       1 |      25 |
| clang-tidy   |      77 |    9157 |         |
| rosecheckers |         |         |     721 |

| zeek         | EXP34-C | EXP33-C | MSC12-C |
|--------------|---------|---------|---------|
| cppcheck     |      53 |      29 |     131 |
| clang-tidy   |      44 |    5225 |         |
| rosecheckers |      17 |         |     480 |

This totals >16,000 alerts! We were planning on testing all alerts, but this is too many to test.  For the bigger categories, we will have to test just a random sample of them.

The test data will be made available, but in a disabled fashion. To enable a test, the tester will:
 1. Enable a single source file, tool, and CERT rule.
 2. Run the test on that source file with a default 'empty' answer file.
 3. If the test generates the correct answer, update the answer file with its answer.
    Otherwise, report a bug.

To complete this test, we do the following:

    For each tool/guideline/codebase,
      Pick N random alerts; N=5 for now. For each alert,
        Manually check if ACR did the right thing:
        (repaired correctly or correctly refused to repair.)
      Until ACR does the Right Thing on >=80% of alerts,
        Fix ACR bugs and re-test.

### Measuring and Improving Satisfactory Alert Redemption

One of our measures of satisfactory alert redemption is done by randomly selecting alerts to manually adjudicate (using web-based random number generators and the number of alerts in the output), manually adjudicating and analyzing if automated repair should be done, then inspecting if our tool automatically and correctly repairs them. Scripts like `data/test/adjudicated_alerts_info_and_repair.py` and `data/test/test_satisfaction_status_tables.sh` help automate the process of running tests on the adjudicated alerts and then gathering overall statistics on satisfactorily handling the adjudicated alerts into tables. The latter table-creating script specifies particular datasets, coding rules, and static analysis tools but those lists can be easily extended or substituted. You can use the scripts to measure satisfactory alert redemption on your own codebases, tools, and code flaw taxonomy items of interest. Results can be used to target efforts to integrate particular code repairs, e.g., if those would eliminate many alerts and/or alerts with code flaws of particular interest.
## “Stumble-Through” Testing

Since there are too many alerts to verify them all, this is a preliminary test to make sure that the repair tool does not crash or hang.

In this test, we run the repair tool on all alerts in all codebases. The test fails if the tool crashes, hangs, or throws exceptions.

For this test, it does not matter whether the tool correctly repairs any alerts. The main point is that the tool contains no bugs or exceptions that prevent us from testing all the alerts.

## Integration Testing

In this scenario, we build an OSS codebase and run its own testing mechanisms. We then repair a subset of alerts on that codebase. We then re-build the codebase and run it through its tests. If the tests behave identically to the un-repaired tests, then our test passes.

The `codebases.yml` file indicates how to build and test each codebase.

The Git testsuite is reliable; but Zeek's testsuite is less reliable. (TODO fill out details)

Before doing this testing, we should complete the Sample Alert Testing for the same rule/tool/codebase.

## Performance Testing

This test confirms that the repairs imposed on code do not significantly impede performance

    Compile original codebases; run their internal testing mechanism.
    Measure the time and usage of the testing mechanisms.
    Run the repair tool on all codebases.
    Compile the repaired codebases; run their internal testing mechanisms.
    Measure the time and usage of the testing mechanisms.

Time should be <5% slower. Memory usage should be equivalent.

## Recurrence Testing

This test confirms that the code has been repaired, according to the SA tools.

    Run the repair tool on all codebases.
    We rerun SA tools on the repaired code.
    The goal is to see if the SA alerts that were repaired disappear. If not, why not?
    We rerun ACR on the repaired code with (new) SA alerts.
    Ideally the SA tool should do nothing.
    Confirm that any alerts for successfully-repaired code are reported by ACR as false positives (as the code is repaired).

These results can also be used to identify bugs in ACR or our test data. (For example, perhaps a repair didn't work, or perhaps the SA tool doesn't recognize the repair.

It is unlikely but possible that a SA tool will continue to report an alert if ACR has repaired the code. If this happens, the ACR when re-run on the repaired code should be able to identify that the alert is a false positive and the code is already repaired.

