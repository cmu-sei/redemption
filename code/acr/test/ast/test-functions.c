// uninitialized
int runFunctionTestA( char a );

int runFunctionTestB( char b ) 
{
  if ( b > 10 ) return -1;
  return 0;
}

// uninitialized
int test( int **varG );

int test2( int **varH ) 
{  
  if ( varH == 0 ) return -1;
  return 0;
}

void test3( int **varI )
{
  if ( varI == 0 ) return;
}

long test4( char ** args, int argc )
{
  if ( argc > 0 ) return 0;
  return -1;
}

int * test5( int * varJ )
{
  if ( *varJ < 10 ) return 0;
  return varJ;
}

int ** test6( int ** varK )
{
  if ( !varK ) return 0;
  return varK;
}