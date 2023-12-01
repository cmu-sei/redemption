#include "acr.h"


int flag = 0;

#define NULL 0

/* Should return 0 upon error */
unsigned int foo1(int* p) {
    if (flag) {
      return 0;
    }
    return *null_check(p, return 0);
}

/* Should return -1 upon error */
int foo2(int* p) {
    if (flag) {
      return -1;
    }
    return *null_check(p, return -1);
}

/* Should return NULL upon error */
char* foo3(char** p) {
    if (flag) {
      return NULL;
    }
    return *null_check(p, return NULL);
}

/* Should do default behavior upon error */
int foo4(int* p) {
    if (flag) {
      flag = 1;
    }
    return *null_check(p);
}
