# Verification that ACR's repairs are good

<legal>  
'Redemption' Automated Code Repair Tool  
  
Copyright 2023 Carnegie Mellon University.  
  
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

## Theory

In theory, we are only repairing code that exhibits Undefined Behavior (UB). Occasionally we are also repairing code that exhibits undesirable but well-defined behavior, such as unsigned integer overflow. 

The ISO C standard (section 3.5.3) defines undefined behavior as:

    behavior, upon use of a nonportable or erroneous program construct or of erroneous data, for which this document imposes no requirements

A program with undefined behavior is difficult to predict and analyze, at least after the UB has been encountered. As noted above, a program with UB is allowed to do anything.   (There is actually some controversy in the ISO C committee over whether this allowance is restricted in time to after the UB is encountered...some believe that UB can, and does, allow programs to behave in unpredictable fashion before the UB is encountered.  This looks like time travel, with the explanation being that an optimizing compiler that detects that a program might encounter UB might rewrite the program and alter its behavior before the UB is encountered.)

Our current model of code repair replaces undefined behavior (UB) with explicit error conditions. We believe that for more normal programs, these repairs never affect normal program behavior, and will turn many vulnerabilities into error conditions that, at worst, cause the program to terminate.

A formal proof of our repairs would be fairly simple, as each repair should be small, and there will be a very small number of possible repairs (currently one) for each alert.

We will assume that the code we are repairing is too large for practical formal proofs to ascertain software assurance.  We will also assume that any code we repair will have a test suite that can serve to detect regressions in code.

Assuming this model holds, our repairs should withstand all regression testing. That is, any tests on program behavior reveal that the program continues to behave correctly through repairs. A regression in testing would reveal a bug in the ACR repair process, or in the repair code that ACR injects.

## EXP34-C (null-pointer repairs)

To repair code with potential null-pointer vulnerabilities, such as:

``` cpp
  memcpy( p, q, size); // p might be NULL
```

we insert null checks:

``` cpp
  memcpy( null_check(p, return -1), null_check(q, return -2), size);
```

The null_check macro is defined as follows:

``` cpp
#define null_check(p_expr, ...)                             \
  ({ typeof(p_expr) _sei_acr_temp_bc_p = (p_expr);          \
    if (!_sei_acr_temp_bc_p) {                                               \
        __VA_ARGS__;                                        \
        printf("Exiting due to detected impending null pointer dereference in file %s, function %s, line %d\n", __FILE__, __func__, __LINE__); \
        exit(1);                                            \
    };                                                      \
    _sei_acr_temp_bc_p;                                     \
  })
```

This code uses the GLibc extension of [embedding statements inside expressions](https://gcc.gnu.org/onlinedocs/gcc-3.3.1/gcc/Statement-Exprs.html).

In this code, if the pointer (`p` or `q`) is not null, it is returned unchanged, and hence passed to `memcpy()`. But if the pointer is null, the macro then executes the optional error code associated with the macro, which returns either -1 or -2 in this example. If there is no optional error code, then the system prints an error message and then terminates the program.

It is a simple matter to formally prove that if the pointer in question not null, that the `null_check()` macro does not change the behavior of the code. The behavior does change if the pointer is null. We hope to elevate the behavior from UB to an explicit error condition.

We intend that all repairs introduced by ACR be as simple as this, and follow the same strategy of elevating UB to an error condition.

## Exceptions

Our current model of code repair replaces undefined behavior (UB) with explicit error conditions. We believe that for more normal programs, these repairs never affect normal program behavior, and will turn many vulnerabilities into error conditions that, at worst, cause the program to terminate.

Assuming this model holds, our repairs should withstand all regression testing. That is, any tests on program behavior reveal that the program continues to behave correctly through repairs. A regression in testing would reveal a bug in the ACR repair process, or in the repair code that ACR injects.

We believe there are exactly three conditions where this model may fail, and our repairs have deleterious effects on program behavior:

### Reliance on UB

In this scenario, the program's expected behavior depends on the UB that our repair seeks to prevent.  That is, the program either intends for the effects of the UB to occur, or the UB occurs, and the program continues on, to behave correctly.  It can be argued that such a program still suffers from a bug, especially if this behavior is undocumented, but the bug might only be revealed by the repair causing undesirable behavior.

A famous example of such code is the [Debian uninitialized read vulnerability](https://randomoracle.wordpress.com/2008/06/07/debianopenssl-vulnerability-subtle-and-fatal-12/).

The only way to detect such a bug is to repair the code and test it sufficiently enough to trigger the regression.  Static analysis can detect alerts indicating undefined behavior, but typically can not determine that some UB is intended by the developers.  Traditional dynamic testing could detect regressions, and this might include the codebase's own test suite.

### Previous UB

In this scenario, the program suffers from undefined behavior that is not repaired, and unrelated to a repair that "causes" a regression.  A program with no undefined behavior will not have such bugs, but it will also have nothing for ACR to repair.

For example, the heap might be corrupted by a use-after-free error, but the error might not not manifest itself for some time. Such errors could be triggered by a code repair.

Again, detecting such bugs is common with regression testing and static analysis.

### Race Conditions

In this scenario, the program does not suffer from undefined behaviors, but suffers from a race condition whose behavior is altered by the extra time imposed by a repair.  These are often rationalized as "inserting repairs would impede performance too much".

For example, a program has 10 ms to execute a function, and normally completes it in 9 ms. But repairs, such as additional null checks, extend the time to 11 ms, causing the function to not complete execution in the required time.  The 10-ms requirement would need to be a bone fide requirement, imposed by some internal engineering process, rather than merely a desire for sufficient performance.

Data races are UB, but general race conditions are not, and are common in embedded code.

We can test how repairs affect the time and memory utilization of code, and we can strive to minimize the hit on performance, but it can not be eliminated.

Detecting if a race condition was altered by repairs would be very difficult. Ideally, any such race conditions or timing requirements should be documented.
