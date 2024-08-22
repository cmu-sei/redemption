
// tests nesting issues that are specifically caused by the assignment of a function pointer
// within the git_config_include
struct config_include_data {
  int (*fn)(const char *, const char *, void *);
};

void git_config_include(const char *var, const char *value, void *data)
{
  struct config_include_data *inc = data;
  int (*fn_to_jfn)(const char *, const char *, void *) = inc->fn;
  fn_to_jfn( var, value, data );
}