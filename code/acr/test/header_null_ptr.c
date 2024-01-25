#include <stdio.h>
#include "header_null_ptr.h"

int main(int argc, char** argv) {
    printf("%i\n", foo());
    int ret = 0;
    int* p_ret = &ret;
    #if 1
        return *p_ret;
    #else
        return 1;
    #endif
}
