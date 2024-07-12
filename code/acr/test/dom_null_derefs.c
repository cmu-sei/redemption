#include <stdlib.h>
#include <stdio.h>

void foo(void) {
    int* p = malloc(sizeof(*p));
    struct FooT {
        int* p;
    } foo;
    foo.p = malloc(2*sizeof(int));
    *p = 3333;
    *foo.p = 4444;
    if (p) {
        *p = 5555;
    }
    if (foo.p) {
        *foo.p = 6666;
    }
    p[0] = 8888;    // Should be marked as dependent, but it isn't, due to imprecision of the static analysis.
    *foo.p = 9999;
    printf("... foo\n");
}

int main(void) {
    foo();
    return 0;
}


