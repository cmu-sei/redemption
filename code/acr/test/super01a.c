#include <stdlib.h>
#include "super01.h"

extern int foo(int* p);

int main() {
    int* p = malloc(sizeof(*p));
    int x = foo(p);
    return **&p + x;
}
