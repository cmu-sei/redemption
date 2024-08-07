# Alert Data Format

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

This document attempts to document the JSON structures that RFP uses
to describe and augment alert data.

## High-level structure

A JSON alert file consists of an array of dictionaries, wherein each
dictionary describes a single alert.  E.g.,

```json
[
  { ...alert1... },
  { ...alert2... },
  ...
  { ...alernN... }
]
```

An alert is represented as a dictionary of string key/value pairs,
hereafter referred to as *fields*.

## List of fields

* `alert_id` : integer

    Identifier for an alert with respect to the list the alert is in.
    This is assigned by the brain to alerts in the alert list passed
    to it in numerical order starting at 1 and is used internally as a
    unique identifier for that alert.

* `ast_id` : integer

    The AST node identifier that the alert has been associated with by
    the brain.

* `checker` : string

    The specific rule the `tool` used to generate the alert.

* `column` : string

    The starting column associated with the alert.

* `end_column` : string

    The ending column associated with the alert.

* `comment` : string

    Commentary useful for Redemption developers.

* `conflicting_repairs` : list

    A list of repairs that were unable to be used due to conflicts.
    Generated by `sup.py`.

* `edits` : list

    A user-generated list of repairs.  Identical to `patch`, but for
    user-generated edits rather than automatically generated edits.
    Used by the glove.

* `file` : string

    The file for which the alert was generated.  This is generally a
    relative path name.

* `issue` : string

    A JIRA issue or issues that are associated with this alert.

* `line` : string

    The line number of the `file` associated with the alert.

* `end_line` : string

    The end line number of the `file` associated with the alert.

* `message` : string

    The message associated with the alert.  This is generally the
    human-readable text generated by the tool from which the alert was
    generated.  This is sometimes used by the brain for
    disambiguation.

* `overlapping_alerts` : list

    A list of repairs that were skipped due to their overlapping.
    Output by `sup.py`.

* `patch` : list

    A list of repairs (edits).

    A repair is a list of `[filename, edit-list]` pairs.  The
    edit-list is a list of `[start, end, replacement]`, where `start`
    and `end` are integer file byte positions, and `replacement` is a
    string.  The `start` and `end` represent a region of the file to
    replace with `replacement`.

* `randomness` : string

    A (usually symbolic) reason this alert was chosen for manual
    analysis. `first five` if the alert was selected (non-randomly)
    for adjudication as one the first five alerts in the file,
    `random` if the alert was selected for adjudication using a random
    number generation process (so far, we've used the random number
    generator here: https://www.random.org/integers/ and made it
    generate 5 numbers between 1 and the total number of alerts in a
    file), and `random and first five` if the alert was selected both
    those ways.

Entries have a different set of meanings and selection methods for the MSC12-C test suite data than they do for the other test suite data. For the MSC12-C test suite data, we initially had a disappointing set of test results (and of randomly selected alerts). To produce more-useful test data, we created a new sample set, reusing some specially-selected alerts from our initial set of randomly-selected alerts, and selecting other new target alerts to adjudicate. The full description of meanings and labels for this MSC12-C data is specified in [MSC12-C.alert.special.selection.md](MSC12-C.alert.special.selection.md).

Labels for the MSC-12C `randomness` field:

* If the alert was originally randomly selected and now not included due to being in a now-excluded category, now the randomness entry is set to `disqualified random`.
* If the alert was originally randomly selected and now included, now the randomness entry is set to `random and sample`.
* If the alert was not previously selected, but is now part of the sample testing, the randomness entry is set to `sample`.
* If the alert was originally selected as part of the sample, then later disqualified, its randomness entry is set to `disqualified sample`
* If the alert was originally randomly selected and now its randomness entry is set to `random` (but not `random and sample`), that means it is not included in the sample set due to being "boring". Such an alert is in a targeted alert category, but one (or more) of the original randomly-selected alerts was chosen for the sample testing set, and this alert was not. 


* `rationale` : string

    Manual analysis of the alert.

* `repairable` : string

    A manual determination as to whether an alert is **practically** repairable, **within the context of our current research project**. If developing an automated repair that integrates into our framework seems feasible and not too much effort given the current stage, capabilities, and milestone commitments of the project, then we may mark this field true. We currently limit repairs to repairs that do not negatively impact code maintainability nor comprehension by code maintainers/developers, so we may mark this field false despite finding a way to fix the alert, if the fix would negatively impact code maintainability or comprehension. This field might be marked false even if an automated repair for the same type of code flaw (and/or same type of code construct that triggers the same static analysis alert) has been developed and published by others (code publication and/or documentation publication). 

* `rule` : string

    The CERT C Coding Standard rule, CWE, or other code flaw taxonomy
    condition associated with this alert.  Used in part by the brain
    to determine the appropriate remediation.

* `satisfactory` : string

    Whether the current automated process generates the desired repair, as specified in the `repairable` field.
    (or lack of repair).

* `skipped_repair` : string

    A reason why a repair was skipped.  Generated by `sup.py`.

* `tool` : string

    The tool whose output was used to generate the alert, or `manual`
    if it was manually generated.

* `verdict` : string

    A manual determination as to whether the current alert actually
    violates the specified rule. This may be `true` (means true
    positive), `false` (means false positive), `true (complex)` (means
    assumed true since it's too complex to determine for certain,
    given our time constraints). 
    For more detail on the adjudication rules and lexicon we developed to enable clear and consistent adjudications, see this paper:
    Svoboda, David, Lori Flynn, and Will Snavely. "Static Analysis Alert Audits: Lexicon & Rules." 2016 IEEE Cybersecurity Development (SecDev). IEEE, 2016.
    Our adjudications use a slightly-revised version of those rules: In this project, if the alert message provides more specificity about the region of the identified code line to adjudicate (e.g., if it specifies a particular variable), we use that information. 

* `why_skipped` : string

    A reason why a repair was skipped.

## Table of field usage

| Field                 | Required | Created By | Used By    |
|:----------------------|----------|:-----------|:-----------|
| `rule`                | yes      | author     | brain      |
| `file`                | yes      | author     | brain      |
| `line`                | yes      | author     | brain      |
| `column`              |          | author     | brain      |
| `end_line`            |          | author     | brain      |
| `end_column`          |          | author     | brain      |
| `tool`                |          | author     | brain      |
| `checker`             |          | author     | brain      |
| `message`             |          | author     | brain      |
| `satisfactory`        |          | author     |            |
| `verdict`             |          | author     |            |
| `repairable`          |          | author     |            |
| `rationale`           |          | author     |            |
| `randomness`          |          | author     |            |
| `issue`               |          | author     |            |
| `comment`             |          | author     |            |
| `ast_id`              |          | brain      |            |
| `alert_id`            |          | brain      | brain, sup |
| `patch`               |          | brain, sup | glove, sup |
| `why_skipped`         |          | brain, sup |            |
| `edits`               |          | author     | glove      |
| `skipped_repair`      |          | sup        |            |
| `overlapping_alerts`  |          | sup        |            |
| `conflicting_repairs` |          | sup        |            |
