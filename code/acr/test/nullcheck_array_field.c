/*
##########
# To test:
##########
cd /host/code/acr/test
cp ../acr.h .
clang nullcheck_array_field.c  # Should have no errors.
*/

#include "acr.h"

int main()
{
  char foo[12] = "01234567890";
  null_check(foo);
}
