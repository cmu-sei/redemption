# Ambiguous Static Analysis

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

When we began this project, we assumed that inferring what code must be changed given a static-analysis (SA) alert would be fairly simple. We just needed to know the CERT rule involved, and the line number. A column number would be nice, but not necessary.

We have seen that SA tools do not handle ambiguity in their output well.

## Toy example

Consider this program:

### Code: `example.c`
```c
1. #include <stdio.h>
2. #include <stdlib.h>
3. 
4. int bar(int **arr, int a, int b) {
5.     if (b) {arr[0] = NULL;}
6.     if (a) {arr = NULL;}
7.     printf("%d\n", arr[0][0]);
8.     return 0;
9. }
```

This code has potential dereference of null pointers on line 7. It is possible for `arr` to be NULL. It is also possible for `arr` not to be NULL, but `arr[0]` might be NULL. 

### An Ideal Solution

Clearly there are two regions that could be null-checked:

#### Code: `example.c`
```c
7.     printf("%d\n", NULL_CHECK(NULL_CHECK(arr)[0])[0]);
```

More precisely, the `arr` array, or its first element `arr[0]` should both be null-checked.  For a repair tool, our best input would be an AST node, either the node the represents `arr` or the node representing the expression `arr[0]`.  Since AST nodes are internal to each compiler, a more suitable output would be a starting line & column, and an ending line & column. Unfortunately, many SA tools provide just a single line and column for each alert.

### Cppcheck

How does Cppcheck handle this code?

``` shell
$ cppcheck --version
Cppcheck 2.9
$ cppcheck example.c 
Checking example.c ...
example.c:7:20: warning: Possible null pointer dereference: arr [nullPointer]
    printf("%d\n", arr[0][0]);
                   ^
...
$
```

Cppcheck notices one of the potential null-pointer problems...but which one?

### Clang-tidy

``` shell
$ clang-tidy --version
Ubuntu LLVM version 16.0.6
  Optimized build.
$ clang-tidy -checks='NullDereference' example.c
...
/host/example.c:7:20: warning: Array access (from variable 'arr') results in a null pointer dereference [clang-analyzer-core.NullDereference]
    printf("%d\n", arr[0][0]);
                   ^~~
...
/host/example.c:7:20: warning: Array access results in a null pointer dereference [clang-analyzer-core.NullDereference]
    printf("%d\n", arr[0][0]);
                   ^~~~~~~~~
...
$
```

Clang-tidy at least notices two potential null-dereferences, and it is capable of indicating multiple tokens using `^---` notation. However, two problems arise:  First, clang-tidy seems to have no API of accessing anything other than its line and column number...to retrieve an 'end' line & column, we would have to parse the `^---` notation. Which is certainly possible, but not easy. The second problem is that the `^---` notation indicates either `arr` or `arr[0][0]`, which suggests that Clang is at best inconsistent about its output, or at worst misleading.


## Solution

We should continue to assume that each alert is associated with exactly one problem. We have previously decided that SA tools need not report every problem, and we will repair the problems they cite, and ignore the problems they do not cite.

We therefore have the problem of obtaining an AST node based on a line number and column number. This is tricky because while each AST node indicates the range of characters it covers, each line + column is covered by multiple AST nodes, and they may not indicate the node that should be repaired, but instead a related node, which might only be related in that it belongs to the same statement as the node to repair.

Furthermore, the problem of identifying the correct AST node depends not just on line and column number, but on the CERT rule and tool, and possibly checker. These data are all encoded within the alert, and our code must consistently identify an AST node that could logically have been indicated by the alert, to analyze for possible repair.

    // Returns the AST ID of the expression that should be repaired according to a.
    // If it can't find appropriate ID, returns a string describing the error
    Result<AST_ID, Error> get_ast_id(Alert a);

This `get_ast_id()` function must delegate to several algorithms depending on the rule, tool, and checker indicated by alert `a`.
