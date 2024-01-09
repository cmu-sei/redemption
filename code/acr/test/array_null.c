#include <stdio.h>
#include <stdlib.h>

int bar(int **arr, int a, int b) {
    if (b) {arr[0] = NULL;}
    if (a) {arr = NULL;}
    printf("%d\n", arr[0][0]);
    return 0;
}
