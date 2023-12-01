#include "acr.h"

#include <stdio.h>
#include <stddef.h>
int main(int argc, char** argv) {
    int x = 0;
    int* p = NULL;
    typedef struct Foo {int z;} Foo;
    Foo foo = {};
    if (argc > 1) {
        x = 1;
        p = &x;
        foo.z = 3;
    }
    printf("x=%i, p=%p, foo.z=%i\n", x,  p, foo.z);
}
