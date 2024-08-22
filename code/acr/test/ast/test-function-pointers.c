// the following is for clang AST to produce output 
// for function pointers, but not for the python AST to 
// consume the JSON output.

char ** (*char_bar)(const int **);
// nested function pointers
long (*foo)(int (*)(short));
int (*bar)(short);
int (*test)(short);
typedef int (*tdtest)(int argc, char ** argv);
