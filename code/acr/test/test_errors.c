
int flag = 0;

#define NULL 0

/* Should return 0 upon error */
unsigned int foo1(int* p) {
    if (flag) {
      return 0;
    }
    return *p;
}

/* Should return -1 upon error */
int foo2(int* p) {
    if (flag) {
      return -1;
    }
    return *p;
}

/* Should return NULL upon error */
char* foo3(char** p) {
    if (flag) {
      return NULL;
    }
    return *p;
}

/* Should do default behavior upon error */
int foo4(int* p) {
    if (flag) {
      flag = 1;
    }
    return *p;
}
