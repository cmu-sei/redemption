# How to Test the Redemption tool
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

## Test Components

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

## Types of Tests and Experiments
### Regression Tests

Verifies that each improvement to the tool does not cause bugs or failures to previously-working code.

#### Procedure

Regression tests are automatically checked by Bamboo after every push.

All regressions are mitigated before changes are merged into the main branch.

See the [regression_tests.md](regression_tests.md) document for technical details on how to run regression tests.

### “Stumble-Through” Tests

Since there are too many alerts to verify them all, this is a preliminary test to make sure that the repair tool does not crash or hang.

#### Procedure

Create empty answer files for every test case.  The easiest way to do this would be to grep answer_file in the relevant json files, and pipe the grep output to touch to create the .ans files.

Then run the tests. The tests might take several hours to complete. But bugs might appear.  Perhaps ACR will crash, or throw exceptions. Create JIRA issues for any such errors.

The test succeeds if they complete with no exceptions or crashes. It does not matter what the output of the tests are; that will be tested separately.

When done, you can eliminate the empty answer files.

### Sample Alert Experiments

In this scenario, we pick a single C file that has 1 or more alerts that we wish to repair. We have ACR repair the alerts, and then compare the repaired source code against an 'answer' source code file. The experiment is successful if the test result matches the answer file.

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

#### Procedure:

To complete this experiment, we do the following:

    For each tool/guideline/codebase,
      Pick N random alerts; N=5 for now. For each alert,
        Manually check if ACR did the right thing:
        (repaired correctly or correctly refused to repair.)
      Until ACR does the Right Thing on >=80% of alerts,
        Fix ACR bugs and re-run this experiment.

Each file has about 5 test cases with randomness=random.  Many of these test cases already are satisfactory, and so they have pre-existing .ans files, and they are regularly tested by our CI process. You can rerun these just to be sure, or you can trust that if the output changes on these test cases, the CI system will warn us of failures.

However, some test cases failed in the past, and those are not tested by our CI process, and they lack an .ans file.  So you'll need to create an empty (stub) .ans file for each test case.  Then rerun the experiments.

For each previously-failed test cases, you'll have output, which may or may not match the (empty) .ans file you created.  Inspect the output file, and if it is correct, then the experiment now succeeds...yay!  In each such case, create a new .ans file for that test case (and push it to the repo), so that our CI system starts regularly testing that case. And mark satisfactory=true for that test case in the appropriate json file.  Note that if the output file indicates that a repair was performed, you'll need to inspect it to make sure the repair is correct.

If a previously-failed test case still fails, it should be marked satisfactory=false (if it isn't already). You should create a new JIRA issue for the failed test case, and indicate the issue number in the issue field for that test case in the json file.

After running test cases, you should update the table above with the ratio of satisfactory test cases to all test cases.  This is the minimal satisfaction ratio (MSR)

 * If the MSR is 100%, that means ACR correctly repairs all of the alerts in that bucket. we are done with it.
 * If the MSR is >80%, that means ACR repairs not all alerts, but enough that we can consider that bucket done.
 * If the MSR is <80%, but the team agrees that fixing remaining bugs would be expensive, then again you can consider this task done.
 * Otherwise, the task is not done. Once the newly-created JIRA issues are fixed, you'll re-run this experiment.
Script outputs two .csv 'tables'. First to fill in ratios values in bottom table, second to determine color (<80% red).  Script is test_satisfaction_status_tables.sh, which is now in the main branch of redemption.public. 

Once deemed correct, sample alerts are preserved and act as regression tests for Bamboo. As with regression tests, any change in behavior of a correct sample alert is mitigated before the change is merged into the main branch.

#### Measuring and Improving Satisfactory Alert Redemption
##### Features

Each test case has a set of explicit features:

 * randomness random
 
This feature suggests alerts that should be considered part of this experiment. We should only consider alerts where randomness=random.

 * verdict (true|false|complex)

A determination of whether the alert indicates a weakness in the code (true), does not indicate a weakness in the code (false), or cannot be adequately audited (complex). Complex verdicts are judged to be true for purposes of this experiment.
 
 * repairable (true|false)
 
Whether we believe the Redemption tool should repair the code, regardless of whether the alert is true or a false positive.
 
 * is-false-positive (true|false)
 
This flag indicates if the Redemption tool determined that an alert is a false positive and thus warrants no repair. We expect this flag to be false if Redemption provided a repair, or provided no repair for other reasons. Ideally this flag correlates with the alert actually being a false positive (even though we are more interested in repairing false positives than identifying them.)
 
 * satisfactory (true|wontfix|false)

We designed the Redemption tool to repair some of the true positives, as well as some of the false positives; we never designed it to repair everything, or intended it to recognize all false positives.

The satisfactory=true means that the tool has performed correctly, providing a correct repair on true positives, and either providing a benign repair on false positives, or providing no repair and identifying correctly that an alert is a false positive.

The satisfactory=wontfix means that while the tool's output is incorrect, the tool has performed exactly as it is designed to do, and we "gave up"; that is, we are not going to improve its behavior.

Finally, satisfactory=false means that the tool's output is incorrect, and we treat this as a bug to fix.

In theory, the experiment is concluded when there are no remaining alerts with satisfactory=false. All alerts we examine will have satisfactory to be true or wontfix.

There is also a feature that can be determined from running the Redemption tool on the test case.

 * patch (empty|nonempty)

Indicates if the Redemption tool actually proposed a repair patch for the code (nonempty).  Alerts from the brain module will contain a 'patch' slot which may be an empty or nonempty list; you can use this to determine the patch feature. Or see if Redemption presented a file distinct from the un-repaired source.

##### Result States

After running Redemption on a test case, we can deem its output to always fit in exactly one of these states.

###### State A: satisfactory=true, verdict=(true|complex)

The code should have been repaired, and Redemption supplied a correct patch.

Implies repairable=true, patch=nonempty

###### State B: satisfactory=true, verdict=false, is-false-positive=true

The alert is a false positive, and Redemption correctly recognized this and provided no repair.

Implies repairable=false, patch=empty

###### State C: satisfactory=true, verdict=false, patch=nonempty

Even though the alert is a false positive, Redemption supplied a correct (non-breaking) patch.

Implies repairable=true

###### State D: satisfactory=wontfix|false, verdict=true|complex, patch=empty

The code should have been repaired, but Redemption provided no repair

For some of these repairable=false and satisfactory=wontfix, which means we did not expect the tool to repair the alert, but it still yields a sub-optimal value.

###### State E: satisfactory=wontfix|false, verdict=false, patch=empty, is-false-positive=false

The alert was a false positive, and Redemption provided no repair. However, Redemption did not acknowledge that the alert was a false positive (and thus its lack of repair was for a completely different reason.)

###### State F: satisfactory=wontfix|false, verdict=true|complex, patch=nonempty

The code should have been repaired, and Redemption provided a patch, but the patch was incorrect.

###### State G: satisfactory=wontfix|false, verdict=false, patch=nonempty

The alert was a false positive, but Redemption provided an incorrect patch.

To qualify for this state, the patch must break the code.

##### Result State Summary

The states were defined based in terms of the verdict, patch, and satisfactory features:

```
    Satisfactory=true
    |                      |      patch=      |
    |                      | nonempty | empty |
    |----------------------+----------+-------|
    | verdict=true|complex |     A    |       |
    | verdict=false        |     C    |   B   |
    |----------------------+----------+-------|

    Satisfactory=false
    |                      |      patch=      |
    |                      | nonempty | empty |
    |----------------------+----------+-------|
    | verdict=true|complex |     F    |    D  |
    | verdict=false        |     G    |    E  |
    |----------------------+----------+-------|
```


Clearly, A+B+C+D+E+F+G=100% of test cases in an experiment.  When we update this test data, we will verify that these states total 100% of alerts in the test case. We will add an assertion to catch this error.

For the experiment to succeed:
 * G == 0 (otherwise our tool has a showstopper bug)
 * A+B+C >= 80% of the test cases (4/5)

```
    |                      |    satisfactory=       |
    |                      |   true | wontfix|false |
    |----------------------+--------+---------------|
    | verdict=true|complex |     A  |        (D, F) |
    | verdict=false        | (B, C) |      (E, G=0) |
    |----------------------+--------+---------------|
    |                      |  >=80% |         <=20% |
```

The test case results of each bucket can be presented as six numbers in the fashion: A-B-C-D-E-F. Success can be indicated by coloring the background green (success) or red (failure).  A, B, and C should be green, they measure success. D, E, and F could be orange, as they measure failure.

##### Technical Details

One of our measures of satisfactory alert redemption is done by randomly selecting alerts to manually adjudicate (using web-based random number generators and the number of alerts in the output), manually adjudicating and analyzing if automated repair should be done, then inspecting if our tool automatically and correctly repairs them. Scripts like `data/test/adjudicated_alerts_info_and_repair.py` and `data/test/test_satisfaction_status_tables.sh` help automate the process of running tests on the adjudicated alerts and then gathering overall statistics on satisfactorily handling the adjudicated alerts into tables. The latter table-creating script specifies particular datasets, coding rules, and static analysis tools but those lists can be easily extended or substituted. You can use the scripts to measure satisfactory alert redemption on your own codebases, tools, and code flaw taxonomy items of interest. Results can be used to target efforts to integrate particular code repairs, e.g., if those would eliminate many alerts and/or alerts with code flaws of particular interest.

<a name="integration-experiments"></a>
### Integration Experiments

In this scenario, we build an OSS codebase and run its own testing mechanisms. We then repair a subset of alerts on that codebase. We then re-build the codebase and run it through its tests. If the tests behave identically to the un-repaired tests, then our experiment is successful.

#### Procedure

For the codebase (git or zeek), build it and run its own testing mechanisms. Then apply the repairs for each tool (cppcheck, clang-tidy, or rosecheckers), and each rule (EXP34-C, EXP33-C, or MSC12-C), creating an 'improved build'. Then re-build the codebase and run it through its tests. If the tests behave identically to the un-repaired tests, then our experiment succeeds.

The `codebases.yml` file indicates how to build and test each codebase.

Before doing this experiment, we should complete the Sample Alert Experiment for the same rule/tool/codebase.

### Performance Experiments

This experiment confirms that the repairs imposed on code do not significantly impede performance

#### Procedure

    Compile original codebases; run their internal testing mechanism.
    Measure the time and usage of the testing mechanisms.
    Run the repair tool on all codebases.
    Compile the repaired codebases; run their internal testing mechanisms.
    Measure the time and usage of the testing mechanisms.

Time should be <5% slower. Memory usage should be equivalent.

### Recurrence Experiments

This test confirms that the code has been repaired, according to the SA tools.

#### Procedure

    Run the repair tool on all codebases.
    We rerun SA tools on the repaired code.
    The goal is to see if the SA alerts that were repaired disappear. If not, why not?
    We rerun ACR on the repaired code with (new) SA alerts.
    Ideally the SA tool should do nothing.
    Confirm that any alerts for successfully-repaired code are reported by ACR as false positives (as the code is repaired).

These results can also be used to identify bugs in ACR or our test data. (For example, perhaps a repair didn't work, or perhaps the SA tool doesn't recognize the repair.

It is unlikely but possible that a SA tool will continue to report an alert if ACR has repaired the code. If this happens, the ACR when re-run on the repaired code should be able to identify that the alert is a false positive and the code is already repaired.

