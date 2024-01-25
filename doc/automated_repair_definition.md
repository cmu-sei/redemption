# What is Automated Repair?

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

The Redemption project strives to automatically repair code that violates a CERT rule.

We focused on what rules are automatically repairable.

The CERT Coding Standards all have a remediation cost. This is a metric that is applied to each guideline.

First, here is the [official definition](https://wiki.sei.cmu.edu/confluence/display/c/How+this+Coding+Standard+is+Organized#HowthisCodingStandardisOrganized-RiskAssessment) of Remediation Cost, from the CERT C Coding Standard:

    Remediation Cost—How expensive is it to comply with the rule?

    | Value | Meaning | Detection | Correction |
    |-------+---------+-----------+------------|
    |     1 | High    | Manual    | Manual     |
    |     2 | Medium  | Automatic | Manual     |
    |     3 | Low     | Automatic | Automatic  |
    |       |         | Manual    | Automatic  |

Clearly the guidelines do not address the remediation cost for any alert that requires manual detection but can be repaired automatically. Unfortunately, there is no further elaboration in the CERT standards as to what constitutes manual vs automatic detection vs correction.

Nonetheless, I would expect all of the rules we believe can be repaired to have a low Remediation Cost value, because we think they can be (mostly) corrected, and they are all automatically detected (perhaps with false positives).

With that said, here are the rules, in order of what should be fixed soonest first:

| Rem Cost | ID      | Title                                                                        | Sev    | Prob     | Pri | Lvl |
|----------+---------+------------------------------------------------------------------------------+--------+----------+-----+-----|
| Medium   | EXP34-C | Do not dereference null pointers                                             | High   | Likely   |  18 |   1 |
| Medium   | EXP33-C | Do not read uninitialized memory                                             | High   | Probable |  12 |   1 |
| Medium   | MSC12-C | Detect and remove code that has no effect                                    | Low    | Unlikely |   2 |   3 |
|----------+---------+------------------------------------------------------------------------------+--------+----------+-----+-----|
| Medium   | MSC13-C | Detect and remove unused values                                              | Low    | Unlikely |   2 |   3 |
| Medium   | EXP12-C | Do not ignore values returned by functions                                   | Medium | Unlikely |   4 |   3 |
| High     | INT31-C | Ensure that integer conversions do not result in lost or misinterpreted data | High   | Probable |   6 |   2 |
| Medium   | EXP19-C | Use braces for the body of an if, for, or while statement                    | Medium | Probable |   8 |   2 |
| Medium   | ERR33-C | Detect and handle standard library errors                                    | High   | Likely   |  18 |   1 |
| High     | INT32-C | Ensure that operations on signed integers do not result in overflow          | High   | Likely   |   9 |   2 |
| High     | DCL00-C | Const-qualify immutable objects                                              | Low    | Unlikely |   1 |   3 |
|----------+---------+------------------------------------------------------------------------------+--------+----------+-----+-----|
| Medium   | DCL01-C | Do not reuse variable names in subscopes                                     | Low    | Unlikely |   2 |   3 |
| Low      | DCL04-C | Do not declare more than one variable per declaration                        | Low    | Unlikely |   3 |   3 |
| Medium   | DCL02-C | Use visually distinct identifiers                                            | Low    | Unlikely |   2 |   3 |
| Medium   | MSC07-C | Detect and remove dead code                                                  | Low    | Unlikely |   2 |   3 |

Quite surprising! In theory, all of these should have Low cost, but only one does (DCL04-C).

## Redemption Assumptions

To understand these differences, here are the assumptions we are making for a CERT rule to be automatically repair-able in the Redemption Project:

 1. The rule need not be automatically detectable. We leave the problem of detecting violations to external tools.
 2. We assume the existence of a 'standard' error-handling mechanism, such as returning NULL, is an adequate solution for un-preventable errors

## Remediation Cost Assumptions

As noted above, the CERT coding standard does not define further the qualifications for a CERT guideline to be "automatically repairable". Perhaps we can suss out its assumptions by examining the guidelines that *are* repairable (i.e. have a Remediation Cost of Low).  Let's look at several CERT guidelines with Low remediation cost:

### DCL04-C. Do not declare more than one variable per declaration

We have already reasoned how to fix this code:

```c
int x, y;
```

can be rewritten as:

```c
int x;
int y;
```

which has the same semantics.  It also involves no error handling.

### MSC30-C. Do not use the rand() function for generating pseudorandom numbers

This can be automatically repaired by replacing each call to `rand()` with the POSIX `random()` or the Windows `BCryptGenRandom()`. This rule also involves no error handling.

There would also be secondary considerations, such as initializing the RNGs properly. This is addressed by MSC32-C:

### MSC32-C. Properly seed pseudorandom number generators

This could be automatically repaired in theory. However, the repair for any MSC32-C alerts is to add proper seeding to the program's beginning, perhaps as the first statement in `main()`,  So the manual repair is cheap enough to not warrant putting effort into automatic repair.

### MEM33-C. Allocate and copy structures containing a flexible array member dynamically

Why is the Rem Cost low here?  I think the theory is that no flexible array member should be allocated on the stack, because the member should be flexible. So it should use the heap. Also don't pass f.a.m's in as function parameters, pass pointers to f.a.m.'s around instead. And don't use =, use memcpy() instead.  But none of this strikes me as easily automatically repairable.

### STR30-C. Do not attempt to modify string literals

Why is the Rem Cost low here? I suspect the theory is that many such examples, such as the first two, can be repaired by taking a char* and changing it to a char[]. That is, a char* (presuambly where the pointer is on the stack) initialized to a string literal becomes a char array, and the literal simply gets initialized on the stack, not the global segment. Strings on the stack can be changed easily.

But the last compliant solution throws that all to hell. Mainly because the strchr() and strrchr() functions take a const char* string and return an element within it with the const cast away.  This is a std C library problem, but the compliant solution can clearly not be automatically generated by repairing the NCCE.

So perhaps the rem cost should be "usually low, but occasionally medium"?

### EXP34-C. Do not dereference null pointers

Remediation Cost=Medium

Our reasoning for fixing this code is:

```c
  x = malloc(1);
  *x;
```

becomes

```c
  x = malloc(1);
  *check_null(x);
```

where `check_null()` is a macro or inline function that indicates an error if `x` is null.  What error it indicates varies on the context, but we will assume that a strategy for handling errors exists.

### Conclusion

First of all, the times when I disagree with the Remediation Cost, I added comments to the CERT wiki. Please review & comment.

The purpose of this analysis was to try to discern the assumptions we made implicitly when determining Remediation Cost Low vs Medium in the CERT guidelines. I would conclude:

 1. If the rule violations cannot be automatically detected, we ignore automatic repair potential, and set the Remediation Cost to High.
 2. If violating the rule generates an error, then an automatic repair mechanism should prevent the error. (In other words, the program should do what the developer intended and not indicate any error from violating the rule.)

## Repairable Code Assumptions

I've added more data:

Scope: how much code has to be changed for the repair to work:
  local = code can be repaired at one or two locations without affecting the rest of the program
  global = a repair might have to modify a variable type. Typically this requires lots of changes throughout the program or it won't compile.
  init = a repair should be done near program initialization (eg a static constructor, or main())

Error:
  yes = a repair requires the ability to report an error in a controlled fashion. IOW the repair converts UB to a controlled error condition
  no = no error involved (or the repair does not mitigate any error)

Pathalogical:
  common = there will be lots of cases where a repair will not work (prob >20%)
  rare = there will be a few cases where a repair will not work (<20%)
  none = no cases where a repair will not work


| Scope  | Error | Pathalogical | Rem Cost | ID      | Title                                                                        |
|--------+-------+--------------+----------+---------+------------------------------------------------------------------------------|
| local  | yes   | none         | Medium   | EXP34-C | Do not dereference null pointers                                             |
| local  | yes   | rare         | Medium   | EXP33-C | Do not read uninitialized memory                                             |
| local  | no    | none         | Medium   | MSC12-C | Detect and remove code that has no effect                                    |
|--------+-------+--------------+----------+---------+------------------------------------------------------------------------------|
| local  | no    | none         | Medium   | MSC13-C | Detect and remove unused values                                              |
| local  | yes   | none         | Medium   | EXP12-C | Do not ignore values returned by functions                                   |
| local  | yes   | none         | High     | INT31-C | Ensure that integer conversions do not result in lost or misinterpreted data |
| local  | no    | none         | Medium   | EXP19-C | Use braces for the body of an if, for, or while statement                    |
| local  | yes   | none         | Medium   | ERR33-C | Detect and handle standard library errors                                    |
| local  | yes   | none         | High     | INT32-C | Ensure that operations on signed integers do not result in overflow          |
| local  | no    | none         | High     | DCL00-C | Const-qualify immutable objects                                              |
| global | no    | rare         |          | CWE-485 | Struct and class members should be private                                   |
|--------+-------+--------------+----------+---------+------------------------------------------------------------------------------|
| local  | no    | rare         | Medium   | DCL01-C | Do not reuse variable names in subscopes                                     |
| local  | no    | none         | Low      | DCL04-C | Do not declare more than one variable per declaration                        |
| local  | no    | rare         | Medium   | DCL02-C | Use visually distinct identifiers                                            |
| local  | no    | none         | Medium   | MSC07-C | Detect and remove dead code                                                  |
|--------+-------+--------------+----------+---------+------------------------------------------------------------------------------|
| local  | no    | rare         | Low      | MSC30-C | Do not use the rand() function for generating pseudorandom numbers           |
| init   | no    | common       | Low      | MSC32-C | Properly seed pseudorandom number generators                                 |
| global | no    | common       | Low      | MEM33-C | Allocate and copy structures containing a flexible array member dynamically  |
| local  | no    | common       | Low      | STR30-C | Do not attempt to modify string literals                                     |

As might be expected, the Redemption project is strongly favoring rules with local fixes.

## Detectable Violation Assumptions

Here we should discern what assumptions in the CERT guidelines were made to determine if a rule is automatically detectable (eg whether the Remediation Cost should be Medium or High.)

### SIG31-C. Do not access shared objects in signal handlers

Why is the Rem Cost high here? It should be easy to inspect a signal handler source code to see if it references any static data, and whether that data is volatile sig_atomic_t. It would still be hard to repair. So the Remediation Cost should be Medium.

### MEM35-C. Allocate sufficient memory for an object

I'm guessing that this is Rem Cost=High because in the general case it would be hard to determine for arrays. For example:

  int *array = malloc(ARRAY_SIZE * sizeof(int)); // assume successful
  array[100] = 1;  / valid?

If the array write is invalid, is that because 100 is not intended to be a valid index (eg ARRAY_SIZE < 100) or is ARRAY_SIZE set to too small a value?

### ARR30-C. Do not form or use out-of-bounds pointers or array subscripts

In the general case, detecting an OOB pointer or subscript requires whole program analysis (and probably solving the halting problem)

### INT30-C. Ensure that unsigned integer operations do not wrap

In the general case, detecting wrapping requires whole program analysis (and probably solving the halting problem)

### INT31-C. Ensure that integer conversions do not result in lost or misinterpreted data

In the general case, detecting wrapping requires whole program analysis (and probably solving the halting problem)

### INT32-C. Ensure that operations on signed integers do not result in overflow

In the general case, detecting overflow requires whole program analysis (and probably solving the halting problem)

### Conclusion

Note that all of these rules have many entries in the 'Automated Detection' section, whiich suggests they may be at least partially detectable

Again, the times when I disagree with the Remediation Cost, I added comments to the CERT wiki. Please review & comment.

The purpose of this analysis was to try to discern the assumptions we made implicitly when determining Remediation Cost Medium vs High in the CERT guidelines. I would conclude:

 1. If the rule violations cannot be automatically detected in the general case, it is marked High (even if there are specific cases where it can be detected)
