int puts(const char *s);

int foo(int* p) {
    if (!p) {
        puts("Error: null pointer!");
        /* Bug here: forgot to return. */
    }
    return *p;
}

