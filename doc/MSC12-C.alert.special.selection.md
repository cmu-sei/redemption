# MSC-12C Alert Special Selection
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

## MSC-12C Alert Special Selection

The `randomness` field in the `alerts.json` test suite data files for the alerts mapped to violations of coding rule MSC12-C are different than those for the other test suite data described in [alert_data_format.md](alert_data_format.md) and [test.md](test.md).

Entries for the `randomness` field have a different set of meanings and selection methods for the MSC12-C test suite data than they do for the other test suite data. For the MSC12-C test suite data, we initially had a disappointing set of test results (and of randomly selected alerts). To produce more-useful test data, generally we created a new sample set, reusing some specially-selected alerts from our initial set of randomly-selected alerts, and selecting other new target alerts to adjudicate.

### Labels and their meanings in the randomness field

Labels for the MSC-12C `randomness` field:

* If the alert was originally randomly selected and now not included due to being in a now-excluded category, now the randomness entry is set to `disqualified random`.
* If the alert was originally randomly selected and now included, now the randomness entry is set to `random and sample`.
* If the alert was not previously selected, but is now part of the sample testing, the randomness entry is set to `sample`.
* If the alert was originally selected as part of the sample, then later disqualified, its randomness entry is set to `disqualified sample`
* If the alert was originally randomly selected and now its randomness entry is set to `random` (but not `random and sample`), that means it is not included in the sample set due to being "boring". Such an alert is in a targeted alert category, but one (or more) of the original randomly-selected alerts was chosen for the sample testing set, and this alert was not. 

### Detail on Alert Special Selection for MSC12-C

Generally, what we did was to filter our initial set of disappointing randomly-selected alerts to remove certain types of alerts. Then, we selected representatives of particular categories of alerts we decided to include. We started this first by checking if there was already at least one such alert in the randomly-selected group. If yes, then at least one of those previously-randomly-selected alerts was reselected. If not, then an alert was selected from the set of target alerts for that target category.

Specifically, for each of the MSC12-C test data files, below we provide our analysis of the alerts in the file, then describe how the sample set was selected, including information about excluded alert categories and targeted alert categories.

#### zeek and cppcheck

103 of the 131 alerts are false and disqualified, and about unused labels.

By "unused labels", we mean there are no `goto` statements directed to the labels. The code was produced by yacc or bison and provided many `goto` labels in order to simulate a state diagram. While we could have tried to remove these labels, we decided that this did not constitute an improvement to the code, and thus we labeled these to be false positives.

This exemplifies a potential hazard of repairing a CERT recommendation: Unlike CERT rules, the nature of recommendations implies that complying with the recommendation might not always improve the code. In theory, we could program Redemption to remove these labels.

For the sample dataset, we selected and adjudicated 5 alerts that are NOT about an unused label. (There were already 2 randomly-selected and adjudicated alerts that were not about an unused label.)

#### git and cppcheck

16 of the 25 alerts are about unused `argc` in: `"argc = parse_options(argc, argv, ...)"`

For the sample dataset, we:

* selected 1 of these 16 for the sample set. (The randomly-selected alerts already included 4.)
* selected and adjudicated 4 more alerts from the remaining 9 alerts out of the 25 alerts. (The randomly-selected alerts already included 1 from this set.)

That provided 5 "diverse" alerts for the sample set (which includes some randomly-selected alerts).

#### rosecheckers

We decided to ignore all rosecheckers MSC12-C alerts and not to try to repair them or analyze their code.
We believe they are all un-repairable. Many of them complain of expressions inside macros (Git and Zeek use multi-line macros extensively), complicating the analysis.
We decided that even if some small number of these alerts are true positives, the high false-positive rate means there is too little value in these alerts to justify repairing them.

Our analysis of the rosecheckers source code (https://github.com/cmu-sei/cert-rosecheckers/blob/main/rosecheckers/MSC.C#L95) MSC12-C checker:  rosechecker's MSC12-C alert only fires on 'expression statements' (a statement that is a full expression). To be flagged, this expression statement must not be the last statement in a basic block. Also, the expression must not be the following types: `Assignment, Conditional, Pointer Dereference, Function Call, delete, addition, subtraction`.

Details are provided below of our original analysis of rosecheckers MSC12-C alerts for zeek and git.

##### zeek and rosecheckers

366 of the 480 alerts have a valid (nonzero) line number.
105 have line number 0, so we consider them "disqualified" and excluded them.
9 alerts were unknown and uncategorized, at that time.

281 of the 366 alerts are about an `assert` function (or a macro), including variants like `ASSERT_UNUSED()`.
85 of the 366 alerts remained beyond that as candidates for the sample set, since they have a valid line number and the line has no assert function.

For the sample dataset, we:

* selected 1 of these 281 (there were 5 such alerts in the original randomly-selected set),
* selected 4 more alerts from the remaining 85 (there were 0 such alerts in the original randomly-selected set)

##### git and rosecheckers

331 of the 721 alerts are about the standard `assert()` macro.
331 of the 721 alerts are about an `error()` or `error_errno()` function.
17 of the 721 are about a `VERIFY_CI()` macro
42 of the 721 alerts are about something besides `assert`s or `error`s or `VERIFY_CI`

For the sample dataset, we:

* selected 1 of the 331 alerts about `assert` (there was 1 such alert in the randomly-selected set)
* selected 1 of the 331 alerts about `error` (there were 4 such alerts in the randomly-selected set)
* selected 1 of the 17 alerts about `VERIFY_CI`
* selected 2 more alerts (ideally about distinct problems)

