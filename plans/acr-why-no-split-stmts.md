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

For the FY18-20 ACR line project, we designed the repairs so that we never need to split an expression into multiple statements.  The reason for this was to avoid complications that arise when modifying the text of the source code at the character level (rather than at the AST level).

As an example, consider the following snippet from coreutils regexec.c (https://github.com/coreutils/gnulib/blob/769c6d033c94ec54cb72c7db2ddcf7d587b5ab37/lib/regexec.c), lines 3549--3554:

```C
    #ifdef RE_ENABLE_I18N
            if (dfa->mb_cur_max > 1)
                bitset_merge (accepts, dfa->sb_char);
            else
    #endif
                bitset_set_all (accepts);
```

Repairing the `bitset_set_all (accepts)` line in a way that splits it into two statements would require insertion of curly brackets.  And for it to work with both possible values of `RE_ENABLE_I18N`, the opening curly brace would need to appear after the `#endif`, not on the same line as the `else` statement.

As another example, consider the following snippet:

```C
    for (int x = foo(); x < bar(); x++) {
        baz();
    }
    int x = 42;
```

Needing to split any of the expressions on the `for` line into multiple statements would require relocating them elsewhere (either inside the body of the loop or outside the loop).

The above examples aren't impossible to split into multiple statements, but splitting does introduce extra complexity that can be avoided by introducing auxiliary functions so that the expressions can be replaced with other expressions instead of splitting into multiple statements.
