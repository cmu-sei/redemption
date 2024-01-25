# Conditional compilation

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

We have decided that the repair tool (like many SA tools and all compilers) will only work on one macro configuration at a time.  It will strive to ensure that repairs made to one configuration will not break other configurations, but if you want to repair multiple configurations, you should provide SA tools that catch errors in configurations other than the one given to the tool.

One thing to note with conditional macros (eg #if/#ifdef/#ifndef directives) is that not all macro configurations are necessarily compile-able. While it is possible to write conditional directives such that all configurations compile, this is often not done. If a program does not compile if FOO is not defined, then the question of how a repair might affect the -UFOO case is itself ill-defined.  Any repair input includes a macro configuration (in the JSON build file) that is known to compile properly. Therefore, if a user wants the program to maintain correctness in macro configurations other than the 'default' one specified, the user should indicate which such configurations compile, somehow.


I will assume that we are going to take an expression, such as

```c
    a+b
```

and replace it with a macro, such as:

```c
    acr_safe_add(a, b, goto handle_error)
```

There are several ways conditional compilation can complicate this:

## 1. Independent

The entire expression occurs with no intervening macro directive:

```c
      x =
    #ifdef WINDOWS
      a+b;   /* expression */
    #else /* LINUX */
      c;
    #endif
```

In this case, the expression can be replaced without affecting any other lines:

```c
      x =
    #ifdef WINDOWS
      acr_safe_add(a, b, goto handle_error);   /* expression */
    #else /* LINUX */
      c;
    #endif
```

## 2. Embedded

A conditional directive is entirely contained inside a sub-expression:

```c
      x =
    #ifdef WINDOWS
      a   /* expression */
    #else /* LINUX */
      c
    #endif
      + b;
```

In this case, the sub-expression can be embedded in the macro without affecting other lines.

```c
      x =  acr_safe_add(
    #ifdef WINDOWS
      a   /* expression */
    #else /* LINUX */
      c
    #endif
      , b, goto handle_error);
```

## 3. Mixed

The conditional directive contains part of the expression that does not match either the Independent or Embedded solutions.

```c
      x =
    #ifdef WINDOWS
      a +   /* expression */
    #else /* LINUX */
      a *
    #endif
      b;
```

In this case, the system would need to intelligently manipulate the macro contents to cover the expression:

```c
      x =
    #ifdef WINDOWS
      a + b  /* expression */
    #else /* LINUX */
      a * b
    #endif
      ;
```

in which case the Independent solution can be used.


## Strategy

My offhand suggestion is that we should build the following function:

```c
    bool isIndependentOfConditionalDirectives(expression, source_code)
```

which takes the expression and returns True if it is independent (that is, it has no conditional macro directives that straddle the expression's boundaries.  The 'expression' is actually a range of bytes in the source code.

For now, if an expression is not independent, we decline to repair it.

If we need to, we can build an `isEmbedded()` function, and do a similar repair.

If we need to, we can build a `transformMixed2Independent()` function, and do a similar repair.


## Examples
### Good Example

In the following snippet (“x = ...”), we could easily do a repair for the “+” operator overflowing; it follows the Embedded pattern.

```c
    #include <stdio.h>

    int main() {
        int x=0, y=0, z=0;
        int a=1, b=2, c=3;

        ////////////////////////////////////////////////////////

        x =
        (
        a
        #if FOO
        * b
        #endif
        ) + c;

        printf("x = %d\n", x);
        return 0;
    }
```

### Bad Example (Syntax)

The following example (“y = ...”) would be more difficult to repair.  This illustrates that just knowing whether a directive precedes or follows an AST node isn’t enough to handle the Embedded case.

```c
    #include <stdio.h>

    int main() {
        int x=0, y=0, z=0;
        int a=1, b=2, c=3;

        ////////////////////////////////////////////////////////

        int* e = &c;

        y = (
        #if FOO
        32);

        z =
        (
        a
        #else
        * e
        #endif
        ) + c;

        printf("y = %d, z = %d\n", y, z);

        ////////////////////////////////////////////////////////

        return 0;
    }
```

#### Rationale

This example is pathological in that the LHS of the + expression depends on whether FOO is defined or not. But you need to parse both -DFOO and -UFOO to discover this.

Under the -DFOO parse, the addition would be seen as mixed, because LHS would be (a), which is partially inside the #if cluase. But under the -UFOO parse, this would be misinterpreted as embedded.

A macro tool (distinct from the current ACR code) could identify pathalogical conditional macros, perhaps by using Clang to build both -DFOO and -UFOO ASTs. It could then put a DANGER sign around this code for ACR to ignore. (Precisely what is ignored can vary; I'm inclined to ignore all repairs around this macro).

### Bad Example (Types)

```c
    #include <stdlib.h>
    #include <stdio.h>

    extern long safe_mul(long x, long y);

    int main(int argc, char** argv) {
        #if FOO
            char *p = calloc(1, sizeof(int));
            typedef long x;
        #else
            if (argc < 3) {abort();}
            long p = atoi(argv[1]);
            long x = atoi(argv[2]);
        #endif

        long ret;
        // Integer-overflow repair for FOO=0 config breaks FOO=1 config.
        ret = (x)*p;
        // Repaired version of above line is:
        // ret = safe_mul((x), p);

        printf("%lx\n", ret);
        return ret;
    }
```

#### Rationale

In this code the type of p depends on whether FOO is defined or not.  As noted, an integer-overflow repair done under -UFOO would butcher -DFOO.

Our distinct macro tool, if it built ASTs under both -DFOO and -UFOO could detect that p is not an integer type under -DFOO, and therefore shut down any repair involving the p variable for the duration of the function.

### Conclusion

I am also thinking that our "pathological macro detection" tool simply does the following:
  1. It takes two compile commands for the same translation unit (.c file). In particular, the commands should differ in which macros are defined and what their values are
  2. It runs the Ear module on both commands, collecting two JSON outputs.
  3. It traverses both outputs looking for diffs. It outputs a list of danger signs, based on the diffs.

The Brain module can take these danger signs and decide not to repair something because it falls within a danger sign.

At least for Year 1 of the project, we could simply decline to repair any subexpressions that contain preprocessor conditional directives or things like #define or #undef. We believe these are rare in real-world code – usually preprocessor directives occur only between statements. This means we will ignore the more pathological cases (like an identifier being a variable in one config but a typedef in another config) that are unlikely to occur in real-world code.  We can detect preprocessor directives inside expressions using our isIndependent() function.
