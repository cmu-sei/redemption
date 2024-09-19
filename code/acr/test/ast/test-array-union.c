char carr[128];

union Data 
{
  int i;
  float f;
  char str[20];
};

union Data instantData;

char * carrarr[20];
char (*carrarrptr)[20];