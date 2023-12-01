#include "acr.h"

#include <stdlib.h>
#include "header_in_subdir/header.h"

int main() {
    int* p = calloc(1, sizeof(int));
    return foo(p) + *null_check(p);
}
