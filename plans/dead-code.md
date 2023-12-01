# Dead Code

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

This is about alerts mapped to MSC12-C. We analyze all the MSC12-C alerts mapped to git or zeek.

## Types of Messages:
### DCL00-C Remappings

As of REM-97 the DCL00-C messages that used to map to MSC12-C should now all map to DCL00-C.

#### DCL00-C Parameter '.*' can be declared as pointer to const

From git:reftable/record.c:245:
    static void hex_format(char *dest, uint8_t *src, int hash_size)
To fix this (in theory), change the line to:
    static void hex_format(char *dest, uint8_t *const src, int hash_size)

This could be remapped to DCL00-C (mark variables not changed as const)

#### DCL00-C Variable '.*' can be declared as const array

From zeek:auxil/broker/caf/libcaf_core/caf/detail/parser/read_floating_point.hpp,75:

     static double powerTable[]
        = {1e1, 1e2, 1e4, 1e8, 1e16, 1e32, 1e64, 1e128, 1e256};

This could be remapped to DCL00-C (mark variables not changed as const)

#### DCL00-C Variable '.*' can be declared as reference to const

A zeek-only (C++?) alert

From zeek:auxil/broker/src/alm/multipath.cc:152:

     auto route = [&](const endpoint_id& id) -> auto& {
        for (auto& mpath : routes)

Presumably mpath should be 'const auto&' (not sure of right syntax)

This could be remapped to DCL00-C (mark variables not changed as const)

### MSC12-C Messages
#### NO_EXAMPLES Label '.*' is not used.

A zeek-only alert, but relevant to C.

auxil/broker/caf/libcaf_core/caf/detail/parser/read_bool.hpp:32
is code that defines a finite state machine, using macros. The important macro is state(), defined in fsn.hpp:42

Can not repair automatically because the label is inside a macro definition. (This applies to all our 'label' alerts!)

#### LOW Assignment of function parameter has no effect outside the function.

From git:builtin/difftool.c:722:

	argc = parse_options(argc, argv, prefix, builtin_difftool_options,
			     builtin_difftool_usage, PARSE_OPT_KEEP_UNKNOWN_OPT |
			     PARSE_OPT_KEEP_DASHDASH);

should be:

	(void) parse_options(argc, argv, prefix, builtin_difftool_options,
			     builtin_difftool_usage, PARSE_OPT_KEEP_UNKNOWN_OPT |
			     PARSE_OPT_KEEP_DASHDASH);

Assignment can be removed, the variable is never read (outside this line).

#### NO_EXAMPLES Redundant assignment of '.*' to itself.
"Redundant assignment of 'yymsp[0].minor.yy528' to itself."

From zeek:auxil/broker/3rdparty/sqlite3.c:165963

Ignore this one, we are not repairing sqlite3.c. (In theory, remove self-assignments)

#### LOW Same expression on both sides of '.*'.

From zeek:auxil/highwayhash/highwayhash/hh_avx2.h:330

    const V4x64U zero = ba ^ ba;

Don't repair, this is a common way to quickly produce 0. (Or perhaps replace with "0").

Line 332 of same file:

    const V4x64U ones = ba == ba;              // FF .. FF

Don't repair, I suspect using 'true' or 1 is incorrect. (Repair should be manual here, something like "~zero")

From zeek:auxil/broker/include/broker/span.hh:157

    return subspan(num_elements - num_elements, num_elements);

Theoretically repair with zero. Not sure this is worth repairing.

In conclusion, I wouldn't repair these automatically, given how few there are. Each repair depends on the operator. The unrepaired code may be nonportable as well.

#### LOW Redundant condition: The condition '.*'' is redundant since '.*' is sufficient.

From zeek:auxil/c-ares/src/lib/ares__parse_into_addrinfo.c:188:

          if (!got_cname || (got_cname && cname_only_is_enodata))

Replace with:

          if (!got_cname || cname_only_is_enodata)
          
since (a || (!a && b)) == a || b

This might be less readable, and it is the only instance.

#### LOW Checking if unsigned expression '.*' is less than zero.

From zeek:auxil/c-ares/src/lib/ares_parse_caa_reply.c:135:

          if (caa_curr->plength <= 0 || (int)caa_curr->plength >= rr_len - 2)

Replace with:

          if (caa_curr->plength == 0 || (int)caa_curr->plength >= rr_len - 2)

However, I am inclined to ignore s/<=0/=0/ repairs, in that <= 0 is (a) harmless (b) makes the code more resillient (in case pLength becomes signed) and (c) easier to read.

#### NO_EXAMPLES Unsigned expression '.*' can't be negative so it is unnecessary to test it.

Only occurs in sqlite3.c, so not fixing.

#### HIGH Redundant initialization for '.*'. The initialized value is overwritten before it is read.

From git:builtin/receive-pack.c:692:

	const char *retval = NONCE_BAD;
    ...
		retval = NONCE_OK;

This is similar to an EXP33-C hazard:

###### Problem: To initialize or not to initialize

Consider this code:

    int x; // uninitialized
    ...
    x = 5; 
    
Solution: If there exists a code path where x is read w/o being initialized, then x should be initialized when declared. This means that EXP33-?C is a true positive and MSC12-C would be a false positive.
On the other paw, if there is no such code path, then that means that after x is declared (whether initialized or not) it is always initialized before being read. This means that EXP33-C is a false positive.
But MSC12-C should also be a false positive.  This is because initializing a variable to a known good value is a good defense-in-depth strategy, and makes the code less brittle, in case the code is later modified to read the value without writing to it first.

In conclusion redundant initializations should never be fixed, but should be treated as false positives for MSC12-C.

#### HIGH Detect and remove code that has no effect

This is the only message produced by rosecheckers...the others are all produced by cppcheck

From git:builtin/am.c:313

	assert(!state->author_name);

Any MSC12-C alert inside an assert statement is a false positive. (perhaps we should fix rosecheckers)
Likewise MSC12-C alerts inside git's 'error(_(' function (macro) are also false positives.

## General Problems
### Problem: Dead code includes a macro conditional
Prominence: Not observed
Example:

  if (cant_happen) {
#ifdef FOO
...
  }

Solution: Should be already dealt with in our conditional macro detection scripts (which might need to be more robust)


### Problem: liveness of code triggered by conditional; removing code could screw up non-default config
Prominence: Not observed
Example:

#ifdef FOO
static int flag = true;
#else
static int flag = false;
#endif

  if (flag) {
  }

Notes: Probably not detectable in the general case.
Solution: We may let user decide this. There may be alert categories where the repair should be disabled by default. But MSC12-C does not seem to suffer from this problem. (prob MSC07-C may be more susceptible).

