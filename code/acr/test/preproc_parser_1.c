int printf(const char *format, ...);

int main() {
    int x=0, y=0, z=0;
    int a=1, b=2, c=3;

    "Hello, I'm a string. ★★★★★";
    "#if FOO #then BAR";
    /* #if FOO */
    // #then BAR

    ////////////////////////////////////////////////////////

    x =
    (
    a
    #if FOO
    * b
    #endif
    ) + c;

    printf("x = %d\n", x);

    ////////////////////////////////////////////////////////

    int* e = &c;

    y = (
    #if FOO
    32);

    z =
    (
    a
    #else
    * e
    #endif
    ) + c;

    printf("y = %d, z = %d\n", y, z);

    ////////////////////////////////////////////////////////

    return 0;
}
