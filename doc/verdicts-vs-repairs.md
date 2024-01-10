# Verdicts vs Repairs

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

For each alert that we use to test ACR, we are making two determinations:

 * Is the alert a true positive? What is its verdict? (a la SCALe)
 * Should ACR repair the alert?
 
One premise of this project is that these two questions are independent. An alert can be a false positive while ACR should (in theory) "repair" the alert. Likewise, ACR may refuse to repair an alert that is a true positive (perhaps repairing it is beyond ACR's capabilities). We hope that 80% of all alerts can either be repaired or determined (by ACR) to be false positives and not worthy of repair.

## Is the alert a true positive?

We traditionally audit alerts using the rules documented in the paper: "Static Analysis Alert Audits: Lexicon \& Rules" (see ../paper/refs.bib for a complete citation). However, based on some code examples below, we have modified the rules slightly.

## Should ACR repair the alert?

This is a yes/no question (or true/false), but is only partially dependent on if the alert is a true or false positive.  In general, if an alert can be determined by ACR to be a false positive, then ACR should not repair it. Likewise, if ACR can determine the alert to be Dependent (on a previous alert), then ACR should not repair it (but should repair the dependent alert).

ACR is a repair tool, not a static-analysis tool. The field of static analysis is full of tools, and it is not a productive use of our time to second-guess pre-existing tools.

### Rule 5

Rule 5 from the paper "Static Analysis Alert Audits: Lexicon \& Rules" states:

    An alert might indicate a true violation of the condition it is mapped to, even if the alert’s message is useless or incorrect.

When performing SCALe audits, we did not have column numbers, and we could ignore messages, focusing exclusively on the CERT rule. Therefore when auditing code, rule 5 would instruct us to mark the alert True if there was any violation of the CERT rule in question.  For SCALe audits performed by an auditor, this was a reasonable demand...an auditor could scan the rest of the line to see if there were any other weaknesses on it.

However, for ACR we have several other constraints: We only occasionally have column numbers. And we always have text messages which can serve to specify where on the line the problem lies. We may have a CWE rather than a CERT rule, and the CWE might be a general one like CWE-398 "Code Quality".  Therefore, we no longer have the luxury of ignoring the message.

Consequently, we would recommend that for this project, the team should use this "alternate rule 5B" which says:

    For an alert to be True, the alert's line number, column number (if supplied, and message should indicate the precise expression that violates the associated condition.

This means that if the column number is supplied, it must point to the location (ideally a single expression) of the problem. If the column correctly does this, then the message is optional. But if the column number is not supplied, the message can be used to point to the location; it can no longer be igored.

### Assertions

The `assert()` keyword's features are somewhat unfortunate.  Assertions are disabled in 'production' builds, which typically have the `NDEBUG` macro defined.  Thus, the decision to disable asserts in production build buys a tiny efficiency boost (the cost of comparing a pointer to NULL), by allowing the production code to have a potential null-dereference, which is a security risk, being undefined behavior, but usually manifests in a crash.

What `assert()` does well is convey developer intent. It indicates that the failure condition is a can't-happen condition, and presumably this has survived development testing (when the `assert()` was actively tested).  When we study insecure code, we have to make assumptions about what the programmer intended, and sometimes it is unclear. But `assert()` makes it clear, while not hindering performance when disabled.

Therefore while an if statement is more secure than an assertion, an assertion is trustworthy when considering a separate problem during an audit. That is, a null-dereference alert would be a false positive if it is preceded by an assertion that the expression cannot be null.  If you have reason to doubt the assert, such as if the program generated an assertion failure, or you can see from the code why an assert might fail, then you can decide differently.  But without contrary evidence, we should treat an assertion as (almost) trustworthy as an if statement.

There is always the concern that an `assert()` might be used to check for a runtime condition, such as an assertion that `malloc()` succeeded.  Such abuses of 'assert()' would betray our trust in assertions.  They also violate CERT rule MSC11-C and should also be repaired when detected; however, that is outside the scope of repairing CERT guidelines besides MSC11-C.

## Examples
### Toy Example (Rule 5B)

Consider this code:

``` c
static void f(void* P1, void* P2, size_t S) {
  memcpy(P1, P2, S);
  /* ... */
}
```

The `memcpy()` function requires that its first and second argument not be NULL.

Suppose we have only one alert for this function. That alert, using its line number, column number, and message, refers to the `P1` pointer in the `memcpy` call. The alert's message says:

    First argument to memcpy, "P1", might be null.
    
We have no other alerts for this code.

Furthermore, suppose that we happen to know that every time this function is called, `P1` cannot be NULL, but `P2` could be.

By rule 5, we would be forced to mark the alert True, even though the null pointer in question is on `P2`, not `P1`. However, our rule 5B requires a different interpretation. Since both the column number and the message indicate that `P1` is the pointer in question, we must adjudicate this alert False.   Furthermore, by failing to have a null-dereference alert for `P2` the ACR would fail to repair that pointer.

### Zeek/Sqlite3 example (Rule 5B, Message disambiguates)

This code appears in zeek/src/3rdparty/sqlite3.c:

``` c
99985    static int memjrnlWrite(
99986      sqlite3_file *pJfd,    /* The journal file into which to write */
99987      const void *zBuf,      /* Take data to be written from here */
99988      int iAmt,              /* Number of bytes to write */
99989      sqlite_int64 iOfst     /* Begin writing at this offset into the file */
99990    ){
99991      MemJournal *p = (MemJournal *)pJfd;
99992      int nWrite = iAmt;
99993      u8 *zWrite = (u8 *)zBuf;
...
99970            assert( pChunk!=0 );
99971            memcpy((u8*)pChunk->zChunk + iChunkOffset, zWrite, iSpace);
...
```

Clang-tidy produces an alert on line 99971, column 9, with this message:

    Null pointer passed to 1st parameter expecting 'nonnull'

The column number is...weird. However, the message clearly indicates that the first argument might be NULL. The SA tool's reasoning is that while there is a NULL check of `pChunk` on line 99970, there is no check on `pChunk->zChunk`. Therefore this alert is a True positive, and ACR should repair it.

### Git example (Message disambiguates)

This code appears in git/builtin/index-pack.c:

``` c
1485    static void rename_tmp_packfile(const char **final_name,
1486                    const char *curr_name,
1487                    struct strbuf *name, unsigned char *hash,
1488                    const char *ext, int make_read_only_if_same)
1489    {
1490        if (*final_name != curr_name) {
1491            if (!*final_name)
1492                *final_name = odb_pack_name(name, hash, ext);
1493            if (finalize_object_file(curr_name, *final_name))
1494                die(_("unable to rename temporary '*.%s' file to '%s'"),
1495                    ext, *final_name);
1496        } else if (make_read_only_if_same) {
1497            chmod(*final_name, 0444);
1498        }
1499    }
```

Clang-tidy produces an alert on line 1497, column 3, with this message:

    Null pointer passed to 1st parameter expecting 'nonnull'"

The column number is...weird. The message makes clear that the first argument to `chmod()` is the problem. However, this parameter `*final_name` still has two potential problems: First, `final_name` could be NULL, and, if it isn't, then `*final_name` could be NULL.  The former problem is Dependent, because if `final_name` were NULL, then it is dereferenced on line 1490, and should be repaired there.  The latter problem is True (unless it can be proven that this function is never called with `final_name` set to NULL). However, the message is clear that NULL might be the parameter passed to `chmod()`, not an operand passed to the `*` operator. Consequently, the latter problem is what the alert refers to. Thus, it is True (or possibly Complex), and ACR should repair it.


### Zeek example (non-returning function)

This code appears in zeek/src/3rdparty/patricia.c:

``` c
373     patricia_tree_t *New_Patricia(int maxbits)
374     {
375       patricia_tree_t *patricia = calloc(1, sizeof *patricia);
376       if (patricia == NULL)
377         out_of_memory("patricia/new_patricia: unable to allocate memory");
378 
379       patricia->maxbits = maxbits;
...
```

Clang-tidy produces an alert on line 379, column 3, with this message:

    Either the condition 'patricia==NULL' is redundant or there is possible null pointer dereference: patricia.

The column number is...weird. The message clearly indicates that `patricia` might be NULL on line 379. The SA tool's reasoning is that while there is a NULL check of `patricia` on line 376, it is possible for the program to call `out_of_memory()` on line 377, resume execution, and dereference NULL on line 379. 

What the tool does not know is that the `out_of_memory()` function does not return; it is defined in auxil/zeekctl/auxil/pysubnettree/patricia.c, line 70, and it ends by calling `abort()` which also does not return.  To infer this, a tool would have to perform "Whole Program Analysis", that is, statically analyze the source code for the entire project, rather than just one file. Some SA tools do this, but not all.

We could endow ACR with Whole Program Analysis by having it trawl through source code ahead of time and produce a list of non-returning functions. Or we could feed a pre-built list to ACR when it repairs code.  We could also write a pre-ACR filter to weed out alerts that are false positives like this one.

In the absence of Whole Program Analysis, an auditor can still see that the alert is False (since `out_of_memory()` never returns). However, ACR should repair it anyway.

We should also promote and encourage the use of the C `_Noreturn` qualifier and C++ `[[noreturn]]` attributes, which should be applied to functions that do not return. These keywords can simplify the work done by static-analysis tools, and our repair code, to determine which functions never return.


### Zeek example (assert())

This code appears in zeek/src/3rdparty/sqlite3.c:

``` c
138597    assert( pSub!=0 );
138598    pSubSrc = pSub->pSrc;
```

Clang-tidy produces an alert on line 138598, column 15, with this message:

    Access to field 'pSrc' results in a dereference of a null pointer (loaded from variable 'pSub')

Consider this hypothetical similar code, where the assertion is replaced with an if statement:

``` c
    if (pSub==0) {printf("Null pointer!\n"); abort();}
    pSubSrc = pSub->pSrc;
```

In this similar code, the alert would clearly be false positive and ACR should not repair the code.

As stated above, we have decided to treat assertions as tantamount to if statements that always succeed (unless there is concrete evidence otherwise). Consequently, in the original code (which used `assert()`), the alert should be deemed false, and ACR should not repair the code.
