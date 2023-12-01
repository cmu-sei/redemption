# Uninitialized variables (EXP33-C)

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

This document shows evidence that different SA tools can report identical alerts but using different lines.

In particular EXP33-C (uninit-var) alerts are reported differently by different SA tools: 
 - Clang-tidy provides the line of code where an uninitialized variable is declared.
 - Cppcheck provides the line where an uninitialized variable is first used.

This suggests that successfully fusing two alerts requires more intelligence than merely identifying that they match CERT rule and line number (and perhaps column number). A by-product of our repair tool would be an "alert canonicalization" tool which would canonicalize alerts that could be fused. By definition, two canonicalized alerts can be fused into one if and only if they have matching CERT rules, line numbers, and column numbers.

## Quick-and-dirty solution

As a quick-and-dirty solution to this problem, we currently ignore the line number in the report and instead grab the name of the uninitialized variable from the message string.  Then we traverse the AST, and when we hit the declaration of the variable, we insert an initializer.

## More-robust solution

The above quick-and-dirty solution fails if two variables in the same function have the same name.  A more robust solution is as follows:

 1. Traverse the AST to find the occurrence of the identifier token at the line and column indicated in the alert.  

 2. If this AST node is a `VarDecl` node, then read its `id` field, create a new `var_decl` field in the alert, and write the value of the AST node's `id` field to the alert's `var_decl` field.

 3. If this AST node is a `DeclRefExpr` node, then find the AST ID of the variable's declaration in the AST node's `referencedDecl` child node, and record this ID in the alert (creating a `var_decl` field).

 4. Traverse the AST again, and when we hit the AST node identified in the alert's `var_decl` field, add an initializer to this AST node.


## Toy example

### Code: `uninit_var.c`
```c
 1. #include <stdio.h>
 2. 
 3. int main(int argc, char** argv) {
 4.     int x;
 5.     if (argc > 1) {
 6.         x = 1;
 7.     }
 8.     printf("x=%i, p=%p, foo.z=%i\n", x,  p, foo.z);
 9. }
```

### Cppcheck

``` shell
$ cppcheck --version
Cppcheck 2.9
$ cppcheck uninit_var.c 
Checking uninit_var.c ...
uninit_var.c:8:33: warning: Uninitialized variable: x [uninitvar]
    printf("The value is %d\n", x);
                                ^
uninit_var.c:5:14: note: Assuming condition is false
    if (argc > 1) {
             ^
uninit_var.c:8:33: note: Uninitialized variable: x
    printf("The value is %d\n", x);
                                ^
$
```

Note that the checker `uninitvar` occurs on the alert for line 8 (the usage of `x`).

### Clang-tidy

``` shell
$ clang-tidy  --version
Ubuntu LLVM version 15.0.7
  Optimized build.
  Default target: x86_64-pc-linux-gnu
  Host CPU: skylake
$ clang-tidy -checks='*' uninit_var.c 
...
/host/uninit_var.c:4:9: warning: variable 'x' is not initialized [cppcoreguidelines-init-variables]
    int x;
        ^
          = 0
/host/uninit_var.c:8:5: warning: 2nd function call argument is an uninitialized value [clang-analyzer-core.CallAndMessage]
    printf("The value is %d\n", x);
    ^                           ~
/host/uninit_var.c:4:5: note: 'x' declared without an initial value
    int x;
    ^~~~~
/host/uninit_var.c:8:5: note: 2nd function call argument is an uninitialized value
    printf("The value is %d\n", x);
    ^                           ~
...
$
```

Note that the checker `cppcoreguidelines-init-variables` occurs on the alert for line 4 (the declaration of `x`).

## Zeek Example

For Zeek, a similar phenomenon occurs on the `qid` variable potentially used before initialization file [`auxil/c-ares/src/lib/ares_query.c`](https://github.com/c-ares/c-ares/blob/2aa086f822aad5017a6f2061ef656f237a62d0ed/src/lib/ares_query.c#L70).  This is a false positive, but determining this requires considering the semantics of `pthread_join`.  The alert is as follows:

### Code: `ares_query.c`
```c
...
 62. static struct query* find_query_by_id(ares_channel channel, unsigned short id)
 63. {
 64.   unsigned short qid;
 65.   struct list_node* list_head;
 66.   struct list_node* list_node;
 67.   DNS_HEADER_SET_QID(((unsigned char*)&qid), id);
 68. 
 69.   /* Find the query corresponding to this packet. */
 70.   list_head = &(channel->queries_by_qid[qid % ARES_QID_TABLE_SIZE]);
...
```

### Cppcheck

```json
  {
    "rule": "EXP33-C",
    "file": "auxil/c-ares/src/lib/ares_query.c",
    "line": "70",
    "column": "41",
    "tool": "cppcheck",
    "checker": "uninitvar",
    "message": "Uninitialized variable: qid"
  },
```

Cppcheck flags line 70 where `qid` is read.

### Clang-Tidy

```json
  {
    "rule": "EXP33-C",
    "file": "auxil/c-ares/src/lib/ares_query.c",
    "line": "64",
    "column": "18",
    "tool": "clang-tidy",
    "checker": "cppcoreguidelines-init-variables",
    "message": "variable 'qid' is not initialized"
  },
```

Clang-tidy flags line 64 where `qid` is declared.



## Model

For auditing and repair, we will assume a specific behavior (as to which line & column is reported) for each tool and checker (and CERT rule).

Which line gets reported by a tool for each CERT rule?

| Rule \ Tool | Clang-tidy        | cppcheck         | rosecheckers     |
|-------------|-------------------|------------------|------------------|
| EXP34-C     | null deredference | null dereference | null is assigned |
| EXP33-C     | uninit var decl   | uninit read      | None             |

