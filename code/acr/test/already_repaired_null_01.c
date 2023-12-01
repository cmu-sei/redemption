#include <stdio.h>
#include <stdlib.h>
#include "/host/code/acr/acr.h"
int foo(int* p) {
    if (!p) {
        puts("Error: null pointer!");
    }
    return *null_check(p);
}
