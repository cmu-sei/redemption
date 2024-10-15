# Recurrence Test Results

We only managed to produce results for Git. Git produced no repairable alerts with rosecheckers, so we only have Git results with clang-tidy and cppcheck, which appear below.

We tried to rerun Cppcheck and Clang-tidy the same way they were run when this project began; that way we could use the results that live in `data/test`. However, we could not reproduce those results precisely. Therefore, we started from scratch, and reran Cppcheck and Clang-tidy on un-repaired Git, ignoring our previous results. 

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

## Git

### Cppcheck

We generated output of Cppcheck 2.9 (manually installed in test container, using the same techniques as in the [Codechecker Docker container](file:../../dockerfiles/codechecker.dockerfile).)

``` bash
cppcheck --enable="all" --force --xml  --project=compile_commands.json  2> cppcheck_bear.xml
```


The following table shows the number of alerts in the un-repaired Git vs. Git with the cppcheck alerts repaired.

| Rule    | Checker                 | Unrepaired | Repaired |
|---------|-------------------------|------------|----------|
| EXP33-C |                         |          1 |        0 |
| EXP34-C |                         |         20 |        7 |
| MSC12-C |                         |         25 |        7 |
|---------|-------------------------|------------|----------|
| MSC12-C | uselessAssignmentArg    |         23 |        7 |
| MSC12-C | redundantInitialization |          2 |        0 |
|---------|-------------------------|------------|----------|
| Total   |                         |         46 |       14 |
|---------|-------------------------|------------|----------|
| All     |                         |        420 |      381 |

32 alerts were repaired
39 alerts disappeared from repair process.
This means 7 non-repairable alerts disappeared without being explicitly repaired. They are:

| Rule    | Checker        | Path                      | Line | Column | Message                                                 | CWE |
|---------|----------------|---------------------------|------|--------|---------------------------------------------------------|-----|
| MSC13-C | unusedFunction | builtin/rev-parse.c       |  660 |      0 | The function 'cmd_rev_parse' is never used.             | 561 |
| MSC13-C | unusedFunction | builtin/unpack-objects.c  |  601 |      0 | The function 'cmd_unpack_objects' is never used.        | 561 |
| MSC13-C | unreadVariable | builtin/sparse-checkout.c |  863 |      7 | Variable 'argc' is assigned a value that is never used. | 563 |
| DCL01-C | shadowVariable | builtin/rev-parse.c       | 1013 |     30 | Local variable 'oid' shadows outer variable             | 398 |
| DCL01-C | shadowVariable | builtin/rev-parse.c       |  709 |      9 | Local variable 'i' shadows outer variable               | 398 |
| DCL01-C | shadowArgument | builtin/unpack-objects.c  |  228 |      7 | Local variable 'type' shadows outer argument            | 398 |
| DCL19-C | variableScope  | builtin/unpack-objects.c  |  460 |     16 | The scope of the variable 'mid' can be reduced.         | 398 |

Also, these new alerts appeared in repaired git but not un-repaired:

| Checker     | Path                     | Line | Column | Message      | CWE  |
|-------------|--------------------------|------|--------|--------------|------|
| syntaxError | builtin/rev-parse.c      |  774 |      5 | syntax error | NONE |
| syntaxError | builtin/unpack-objects.c |  240 |      2 | syntax error | NONE |

However, these alerts did not prevent the repaired build from succeeding, so they seem to be a bug in cppcheck)
And these alerts correspond to no new CERT rule.

All files with disappearing un-repaired alerts had at least one repair. So the repairs seemed to have good additional effects on the files.

As expected, re-running Redemption on repaired git repaired nothing.

### Clang-tidy

We generated output of clang-tidy 16 (already installed in test container).

``` bash
grep --color=none '"file":' compile_commands.json | sed 's/"file"://;  s/",/"/;' | sort -u  | xargs clang-tidy -checks='*'  > clang-tidy.txt
```

The following table shows the number of alerts in the un-repaired Git vs. Git with the cppcheck alerts repaired.

| Rule    | Unrepaired | Repaired |
|---------|------------|----------|
| EXP33-C |       9157 |      500 |
| EXP34-C |         77 |       16 |
| MSC12-C |          0 |        0 |
|---------|------------|----------|
| Total   |       9234 |      516 |
|---------|------------|----------|
| All     |      49558 |    40840 |

8718 alerts were repaired.
8718 alerts disappeared from repair process.
This means that 0 non-repairable alerts disappeared without being explicitly repaired!

As expected, re-running Redemption on repaired git repaired nothing.
