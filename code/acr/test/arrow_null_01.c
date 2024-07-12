#include <stddef.h>

void *malloc(size_t size);

struct my_type  { int i; };

union  my_union { int i; float f;};

int main() {
    int *array = malloc(sizeof(int) * 5); int *array2 = malloc(sizeof(int) * 5); int *array3 = malloc(sizeof(int) * 5);
    array[0] = 777;  // might be a null-pointer deref here if malloc return NULL
    0[array2] = 999;  // lol, this is valid C code
    struct my_type *foo = malloc(sizeof(struct my_type));
    foo->i = 888; // might be a null-pointer deref here if malloc return NULL
    union my_union *bar = malloc(sizeof(union my_union));
    bar->i = 444; // might be a null-pointer deref here if malloc return NULL
    *array3 = 333;
}
