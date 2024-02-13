#include <stdio.h>
#define NULL 0
int flag = 0;

/* Should return 0 upon error */
unsigned int foo1(int* p) {
  int* q = NULL;
  if (flag) {
    return 0;
  }
  printf("q is %d\n", *q);
  return *p;
}

/* Should return -1 upon error */
int foo2(int* p) {
  int* q = NULL;
  if (flag) {
    return -1;
  }
  printf("q is %d\n", *q);
  return *p;
}

/* Should return NULL upon error */
char* foo3(char** p) {
  int* q = NULL;
  if (flag) {
    return NULL;
  }
  printf("q is %d\n", *q);
  return *p;
}

/* Should do default behavior upon error */
int foo4(int* p) {
  int* q = NULL;
  if (flag) {
    flag = 1;
  }
  printf("q is %d\n", *q);
  return *p;
}

int main() {
  int i = 0;
  char *s = "Hello, world";
  printf("foo1() returns %ud\n", foo1(&i));
  printf("foo2() returns %d\n", foo2(&i));
  printf("foo3() returns %s\n", foo3(&s));
  printf("foo4() returns %d\n", foo4(&i));
  return 0;
}
