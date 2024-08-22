
// issue and details can be viewed here:
// https://issues.cc.cert.org/jira/browse/REM-231?focusedId=169412&page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel#comment-169412
typedef char *pc;

pc getPC(void) {
  pc x;
  return x;
}

typedef struct {
  int i;
} s, *ps;

s getS(void) {
  s x;
  return x;
}

ps getPS(void) {
  ps x;
  return x;
}