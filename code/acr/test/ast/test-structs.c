struct TestStructInner
{
  int tsia;
  int * tsib;
  char * tsic;
};

struct TestStructOuter
{
  struct TestStructInner * tsoa;
  int * tsob;
  char * tsoc;
  struct TestStructInner * tsod;
};

struct TestStructInner * testA( struct TestStructOuter * tso )
{
  if ( tso->tsoa ) return tso->tsoa;
  return tso->tsod;
}
