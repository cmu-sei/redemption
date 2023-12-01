# Why some null dereference alerts should remain unfixed (EXP34-C)

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

Having examined several null deference alerts in OSS, we have noted that several alerts are deemed to have a verdict of True, and thus can & should be repaired. However, we believe that the OSS maintainers would argue that they should not be automatically repaired.  This document attempts to enumerate and describe the reasons why such alerts ought not to be repaired, along with code examples.

## Hidden non-nullability model

In this case, there exists an invariant that a pointer must not be null. The invariant may or may not be written down. For example, a struct might contain a character array that always contains a null-terminated byte string (NTBS). There exists a constructor function through which all objects of this struct receive a valid NTBS; consequently the array is never null-checked throughout the program, nor should it be.

### Toy Code:
```c
struct s {
  char* name;
}

struct s* init() {
  struct s* retval = malloc(sizeof(struct s));
  if (retval == NULL) {abort();}
  retval->name = "foo";
  return retval;
}

void foo(struct s *data) {
  if (data == NULL) {abort();}
  printf("The data is named %s\n", data->name); // no null check required
}
```

### TODO Git Example Code
```c
```

### Solution

Ideally, a static-analysis tool would be informed about which pointers must not be null, and would censor their own null dereference alerts accordingly.  This could be done by a separate tool, which filters out null-dereference alerts based on suitable inputs about which pointers are null.

## Implicit performance model

In this case, a null pointer might conceivably sneak into a function that is not equipped to handle it, causing the pointer to be dereferenced. However, the developers may have a policy (again possibly implicit) of not modifying the particular code...perhaps they would agree that a null check should be added, but elsewhere in the code.  Perhaps this because they do not know how to handle a null-dereference error condition.

### Toy Code:
```c
void my_strlen(const char* s) {
  size_t retval = strlen(x);  // null dereference possible, but should be fixed elsewhere
  printf("The length of %s is %uz\n", s, retval);
  return retval;
}
```

### TODO Git Example Code
```c
```

### Solution

Since the average developer can not modify the standard library, and hence add null checks to standard library functions like strlen(), static-analysis tools must keep a list of functions that take non-nullable pointers as a rguments (and cannot be repaired).  Ideally, a static-analysis tool would allow developers to extend such a list with their own functions whose arguments should be non-null, but do not validate their arguments.  (Again, this could be done by a separate tool).

## Annotating Null-able and non-null-able pointers

Clang supports several attributes regarding nullability:
https://clang.llvm.org/docs/AttributeReference.html#nullability-attributes

A proposal to add 'null-able' pointers to ISO C. (Current pointers could then be interpreted as non-null-able in implementations, but this would be a breaking change.)
https://itnext.io/why-c-needs-a-new-type-qualifier-61ad553cbe71

