#include "acr.h"

#include <stdlib.h>
#include <stdio.h>

const char* foo();

int main(int argc, char** argv) {
    char* p = NULL;
    if (argc >= 2) {
        p = argv[1];
    }
    printf("Hello, %s\n", foo());
    return *null_check(p);
}

