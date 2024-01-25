# ACR Requirements & Architecture

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

## Requirements

See [conditional compilation](conditional_compilation.md) for details about how we will address #ifdefs and other macro fun.

### General

Any source file that is repaired should receive an extra inclusion, such as

```c
    #include <acr.h>
```

The acr.h file can be available system-wide and have any macros or inline functions, etc that we decide the repair should have.

Clearly, a source file should not receive this extra inclusion if it already has it.

Each macro defined in acr.h can use the GCC extension of allowing statements inside expressions (which Clang also supports).

Each macro should only be applied if ACR can not already determine that the code is safe. This should include if the macro has already been applied.

### Errors

Each ACR macro would take an <ERROR> variable which indicates what to do if the code would generate an error. ACRE will determine the correct error routine for each function. It could default to something drastic like `abort()`.  Other valid valies might be something like `goto fail`, or `return NULL`.

### Integer Overflow

ACR should resolve

```c
    A + B
```

to

```c
    ACR_SAFE_ADD( A, B, <ERROR>)
```

This presumes that A and B are expressions that evaluate to integers (not floats or pointers).

The following operators would have analogous macros

| Op | Name           | Replacement         |
|----|----------------|---------------------|
| +  | Addition       | ACR_SAFE_ADD        |
| \- | Subtraction    | ACR_SAFE_SUBTRACT   |
| *  | Multiplication | ACR_SAFE_MULTIPLY   |
| << | Left Shift     | ACR_SAFE_LEFT_SHIFT |

The definition of the ACR_SAFE_ADD() macro would be provided in <acr.h>. The macro would test if the addition was safe. If not it would invoke the <ERROR> routine.

### Null Dereference

ACR should resolve any pointer dereference

```c
    *P
```

to

```c
    *(ACR_NOT_NULL(P, <ERROR>)
```

This presumes that P is an expression that evaluates to a pointer.  It would also apply to pointer arithmetic:

```c
    P[I]
```

to

```c
    ACR_NOT_NULL(P, <ERROR>)[I]
```

The definition of the ACR_NOT_NULL() macro would be provided in <acr.h>. The macro would test if P was null and invoke the error if so.

If a pointer is dereferenced multiple times, only the first one (dominating) should be null-checked.

### Integer Conversion

ACR should resolve any integer conversion where the converted-to type might not be able to represent all the values in the converted-from type.

```c
    X = Y;
```

to

```c
    X = ACR_CONVERT(Y, TYPEOF(X), <ERROR>)
```

This would also include explicit casts, and implicit casts for functions.

```c
    void function(INTTYPE X);
    ...

    function(Y);
```

to

```c
    function(ACR_CONVERT(Y, INTTYPE, <ERROR>)
```

The definition of the ACR_CONVERT() macro would be provided in <acr.h>. The macro would test if P was null and invoke the error if so.


## Architecture

See quarterly review slides for the architecture

### Ear

Old ACR repository name: "clang-parser"

This module uses clang to produce a Clang AST from source file, and serializes it to JSON.
Old ACR uses SEI-internal JSON serializer, which only handles C (no C++).

This module should not fail unless Clang itself fails (eg if source file is ill-formed)

This module can be in Python, but it will call the clang-parser, which is C++. Python module can do other things.

Clang also can do many semantic-analysis routines; we may wish to perform some of them and serialize their output in the JSON. Will add as needed.

While old ACR also produced IR, we are currently not planning on going to IR...we will restrict ourselves to AST (plus whatever semantic analysis we need).

### Brain

Old ACR repository name: "memsafety-fr"

This is a Python script that deserializes JSON into Python data structures (dictionaries?). It decides what repairs need to be made.  It outputs original JSON along with "repair instructions".

This module should not fail. However, it should output a log of which repairs it can make and which it can't. (Possibly, it might decide no repairs can be done.)

Old ACR worked with the IR rather than AST. However, this had some bugs going back to the AST. For example, the following code expressions were indistinguishable:

```c
    x == y
    (x = y)
    ((x == y))
```

Knowing when to add parentheses back to the AST was tricky and bug-prone.  So we are going to ignore the IR (for now).

Old ACR did use AST for de-fattening pointers, so we have some working code.

### Hand

Old ACR repository name: "make-monitoring"

A module that takes output JSON with repair instructions and repairs the source code.
Currently Python, but could be C++.
Currently, all repairs are SEI-internal code.
