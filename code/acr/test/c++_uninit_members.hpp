struct Base {
  int x;
  Base() : x(1) {}
  Base(int _x) : x(_x) {}
};

struct D : Base {
  Base s1;
  int a;
  Base s2;
  int b;
  Base s3;
  int c;
  Base s4;
  D();
  D(int);
  D(float);
  D(char);
  D(int*);
  D(float*);
  D(char*);
};
