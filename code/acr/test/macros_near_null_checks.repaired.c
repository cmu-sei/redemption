#include "acr.h"

int printf(const char *format, ...);
void exit(int status);

#define mac_add(x, y) ((x) + (y))
#define mac_deref(p) (*(p))
#define mac_star *

int main(int argc, char** argv) {
    int arr[] = {10, 20, 30, 40, 50, 60, 70, 80, 90};
    int* p = arr;
    if (argc > 1) {
        p = (int*)0;
    }
    printf("%d\n", *null_check(p));
    p = arr + 1; printf("%d\n", mac_add(*p, 1));
    printf("%d\n", *null_check((mac_add(p, 2))));
    printf("%d\n", *mac_add(p, 3));
    printf("%d\n", mac_add(*mac_add(p, 4), 1));
    p = arr + 5; printf("%d\n", mac_deref(p));
    p = arr + 6; printf("%d\n", mac_star p);
}

