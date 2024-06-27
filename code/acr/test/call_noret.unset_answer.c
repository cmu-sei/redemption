#include "acr.h"

#include <stdlib.h>
#include <stdio.h>

void die(char* msg) {
    printf("%s", msg);
    exit(1);
}

int main(int argc, char** argv) {
    int* p;
    if (argc <= 1) {
        die("Too few args!\n");
    } else {
        p = malloc(1);
        if (!p) {abort();}
        *p = argc;
    }
    return *null_check(p);
}
