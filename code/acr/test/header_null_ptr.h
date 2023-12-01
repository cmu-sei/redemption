#include <stdlib.h>

#define FOO 1

static inline int foo() {
    #if FOO
        int *p = calloc(1, sizeof(int));
    #else
        int p;
    #endif
    int *x = calloc(1, sizeof(int));
    return *x + (
        #if FOO
            *
        #else
            1 +
        #endif
            p
    );
}
