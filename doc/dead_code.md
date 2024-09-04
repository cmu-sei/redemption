# Dead Code

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

## Introduction

The [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard) contains three recommendations pertaining to dead code.

 * [MSC07-C. Detect and remove dead code](https://wiki.sei.cmu.edu/confluence/x/6tYxBQ)
 * [MSC12-C. Detect and remove code that has no effect or is never executed](https://wiki.sei.cmu.edu/confluence/x/5dUxBQ)
 * [MSC13-C. Detect and remove unused values](https://wiki.sei.cmu.edu/confluence/x/39UxBQ)

This document is about alerts that are mapped to MSC12-C. We analyze all the MSC12-C alerts mapped to git or zeek.  We did not target alerts mapped to MSC07-C or MSC13-C, although some alerts might have been included in our analysis...not all SA tools broke down dead code in the same way as the SEI CERT standard.

### Analysis

Here we analyze and categorize all the alerts produced for git or zeek that pertain to MSC12-C.

For each category of alerts, we can assign it an attribute:

| Attribute   | Meaning                                                    |
|-------------|------------------------------------------------------------|
| NO_EXAMPLES | There are no examples that we should repair                |
| LOW         | There is repairable code and repairing it is low priority  |
| HIGH        | There is repairable code and repairing it is high priority |

#### Categories

For these categories, we ignored alerts in sqlite3.c, mainly because sqlite3.c is external to zeek.

##### NO_EXAMPLES Label '.*' is not used.

A zeek-only alert, but relevant to C.

auxil/broker/caf/libcaf_core/caf/detail/parser/read_bool.hpp:32
is code that defines a finite state machine, using macros. The important macro is `state()`, defined in fsn.hpp:42

We cannot repair automatically because the label is inside a macro definition. (This applies to all our 'label' alerts!)

##### LOW Assignment of function parameter has no effect outside the function.

From git:builtin/difftool.c:722:

``` c
argc = parse_options(argc, argv, prefix, builtin_difftool_options,
             builtin_difftool_usage, PARSE_OPT_KEEP_UNKNOWN_OPT |
             PARSE_OPT_KEEP_DASHDASH);
```

should be:

``` c
(void) parse_options(argc, argv, prefix, builtin_difftool_options,
             builtin_difftool_usage, PARSE_OPT_KEEP_UNKNOWN_OPT |
             PARSE_OPT_KEEP_DASHDASH);
```

Assignment can be removed, the variable is never read (outside this line).

However, git often used `argc` to indicate the number of program arguments that have not yet been processed, and this invariant was important to developers even if `argc` is never subsequently read. Therefore while removing the assignment is safe, it is not uncontroversial.

##### NO_EXAMPLES Redundant assignment of '.*' to itself.
"Redundant assignment of 'yymsp[0].minor.yy528' to itself."

From zeek:auxil/broker/3rdparty/sqlite3.c:165963

Ignore this one, as it is in sqlite3.c. (In theory, we would remove self-assignments)

##### LOW Same expression on both sides of '.*'.

From zeek:auxil/highwayhash/highwayhash/hh_avx2.h:330

``` c
const V4x64U zero = ba ^ ba;
```

Don't repair, this is a common way to quickly produce 0. (Or perhaps replace with "0").

Line 332 of same file:

``` c
const V4x64U ones = ba == ba;              // FF .. FF
```

Don't repair, I suspect using `true` or 1 is incorrect. (Repair should be manual here, something like `~zero`)

From zeek:auxil/broker/include/broker/span.hh:157

``` c
return subspan(num_elements - num_elements, num_elements);
```

Theoretically repair with zero. Not sure this is worth repairing.

In conclusion, I wouldn't repair these automatically, given how few there are. Each repair depends on the operator. The unrepaired code may be nonportable as well.

##### LOW Redundant condition: The condition '.*'' is redundant since '.*' is sufficient.

From zeek:auxil/c-ares/src/lib/ares__parse_into_addrinfo.c:188:

``` c
if (!got_cname || (got_cname && cname_only_is_enodata))
```

Replace with:

``` c
if (!got_cname || cname_only_is_enodata)
```

since `(a || (!a && b)) == a || b`

This might be less readable, and it is the only instance.

##### LOW Checking if unsigned expression '.*' is less than zero.

From zeek:auxil/c-ares/src/lib/ares_parse_caa_reply.c:135:

``` c
if (caa_curr->plength <= 0 || (int)caa_curr->plength >= rr_len - 2)
```

Replace with:

``` c
if (caa_curr->plength == 0 || (int)caa_curr->plength >= rr_len - 2)
```

However, I am inclined to ignore s/<=0/=0/ repairs, in that <= 0 is (a) harmless (b) makes the code more resillient (in case pLength becomes signed) and (c) easier to read.

##### NO_EXAMPLES Unsigned expression '.*' can't be negative so it is unnecessary to test it.

Ignore this one, as it is in sqlite3.c. (In theory, we remove expressions that test negativity.)

##### HIGH Redundant initialization for '.*'. The initialized value is overwritten before it is read.

From git:builtin/receive-pack.c:692:

``` c
const char *retval = NONCE_BAD;
...
    retval = NONCE_OK;
```

This is similar to an EXP33-C hazard:

###### Problem: To initialize or not to initialize

Consider this code:

``` c
int x; // uninitialized
...
x = 5;
```

Solution: If there exists a code path where `x` is read w/o being initialized, then `x` should be initialized when declared. This means that the EXP33-C alert is a true positive and MSC12-C would be a false positive.
On the other paw, if there is no such code path, then that means that after `x` is declared (whether initialized or not) it is always initialized before being read. This means that EXP33-C is a false positive.
But MSC12-C should also be a false positive.  This is because initializing a variable to a known good value is a good defense-in-depth strategy, and makes the code less brittle, in case the code is later modified to read the value without writing to it first.

In conclusion redundant initializations should never be fixed, but should be treated as false positives for MSC12-C.

##### HIGH Detect and remove code that has no effect

This is the only message produced by rosecheckers...the others are all produced by cppcheck

From git:builtin/am.c:313

``` c
assert(!state->author_name);
```

Any MSC12-C alert inside an assert statement is a false positive. (perhaps we should fix rosecheckers)
Likewise MSC12-C alerts inside git's `error(_(` function (macro) are also false positives.

#### Conclusions

From studying at these alerts, we have identified the following common problems:

##### Problem: Dead code includes a macro conditional
Prominence: Not observed
Example:

``` c
  if (cant_happen) {
#ifdef FOO
...
  }
```

Solution: Should be already dealt with in our conditional macro detection scripts (which might need to be more robust). See our [conditional compilation](conditional_compilation.md) document for more information.

##### Problem: liveness of code triggered by conditional; removing code could screw up non-default config
Prominence: Not observed
Example:

``` c
#ifdef FOO
static int flag = true;
#else
static int flag = false;
#endif

  if (flag) {
  }
```

Notes: Probably not detectable in the general case.
Solution: We may let the user decide this. There may be alert categories where the repair should be disabled by default. But MSC12-C does not seem to suffer from this problem. (Perhaps MSC07-C alerts may be more susceptible).

## MSC12-C Selection Criteria

In our [alert data format](alert_data_format.md) and [test](test.md) documents, we describe our process of selecting alerts to try to repair.  Selection is indicated by the `randomness` field in the `alerts.json` test suite data files.  As those document indicate, the selection should be random.

But the alerts mapped to MSC12-C had to undergo different selection than alerts for the other CERT guidelines. Consequently, entries for the `randomness` field have a different set of meanings and selection methods for the MSC12-C test suite data than they do for the other test suite data. For the MSC12-C test suite data, we initially had a disappointing set of test results (and of randomly selected alerts). To produce more-useful test data, we created a new sample set, reusing some specially-selected alerts from our initial set of randomly-selected alerts, and selecting other new target alerts to adjudicate.

### Labels and their meanings in the randomness field

The following table indicates the value of the `randomness` field for MSC12-C alerts:

| Label               | Meaning                                                                            |
|---------------------|------------------------------------------------------------------------------------|
| disqualified random | Originally selected but no longer included due to being in a now-excluded category |
| random and sample   | Originally selected and remains included                                           |
| sample              | Not previously selected, but now part of the sample testing                        |
| disqualified sample | Originally selected but later disqualified                                         |
| random              | Originally selected, but no longer included due to being "boring"                  |

An alert with `randomness=random` is in a targeted alert category, but one (or more) of the original randomly-selected alerts was chosen for the sample testing set, and this alert was not. 

### Details on Special Selection for MSC12-C

Generally, what we did was to filter our initial set of disappointing randomly-selected alerts to remove certain types of alerts. Then, we selected representatives of particular categories of alerts we decided to include. We started this first by checking if there was already at least one such alert in the randomly-selected group. If yes, then at least one of those previously-randomly-selected alerts was reselected. If not, then an alert was selected from the set of target alerts for that target category.

Specifically, for each of the MSC12-C test data files, below we provide our analysis of the alerts in the file, then describe how the sample set was selected, including information about excluded alert categories and targeted alert categories.

#### zeek and cppcheck

103 of the 131 alerts are false and disqualified, and about unused labels. (`Label '.*' is not used`)

By "unused labels", we mean there are no `goto` statements directed to the labels. The code was produced by yacc or bison and provided many `goto` labels in order to simulate a state diagram. While we could have tried to remove these labels, we decided that this did not constitute an improvement to the code, and thus we labeled these to be false positives.

This exemplifies a potential hazard of repairing a CERT recommendation: Unlike CERT rules, the nature of recommendations implies that complying with the recommendation might not always improve the code. In theory, we could program Redemption to remove these labels.

For the sample dataset, we selected and adjudicated 5 alerts that are NOT about an unused label. (There were already 2 randomly-selected and adjudicated alerts that were not about an unused label.)

#### git and cppcheck

16 of the 25 alerts are about an unused `argc` in:

``` c
argc = parse_options(argc, argv, ...);
```

The messages were `Assignment of function parameter has no effect outside the function.`

For the sample dataset, we:

* selected 1 of these 16 for the sample set. (The randomly-selected alerts already included 4.)
* selected and adjudicated 4 more alerts from the remaining 9 alerts out of the 25 alerts. (The randomly-selected alerts already included 1 from this set.)

That provided 5 "diverse" alerts for the sample set (which includes some randomly-selected alerts).

#### rosecheckers

We decided to ignore all rosecheckers MSC12-C alerts and not to try to repair them or analyze their code.
We believe they are all un-repairable. Many of them complain of expressions inside macros (Git and Zeek use multi-line macros extensively), complicating the analysis.
We decided that even if some small number of these alerts are true positives, the high false-positive rate means there is too little value in these alerts to justify repairing them.

Our analysis of the rosecheckers [source code](https://github.com/cmu-sei/cert-rosecheckers/blob/main/rosecheckers/MSC.C#L95)'s MSC12-C checker reveals the following:  

rosechecker's MSC12-C alert only fires on 'expression statements' (a statement that is a full expression). To be flagged, this expression statement must not be the last statement in a basic block. Also, the expression must not be the following types: `Assignment, Conditional, Pointer Dereference, Function Call, delete, addition, subtraction`.

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

