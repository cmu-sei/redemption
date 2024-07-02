#include "acr.h"

#include "c++_uninit_members.hpp"

struct A : Base {
  Base s1;
  int a = 0;
  Base s2;
  int b = 0;
  Base s3;
  int c = 0;
  Base s4;
  A() = default;
  A(int)    : b(2), c(3) {}
  A(float)  : a(1), c(3) {}
  A(char)   : a(1), b(2) {}
};

struct B : Base {
  Base s1;
  int a = 0;
  Base s2;
  int b = 0;
  Base s3;
  int c = 0;
  Base s4;
  B(int)    : Base(-1), b(2), c(3) {}
  B(float)  : Base(-1), a(1), c(3) {}
  B(char)   : Base(-1), a(1), b(2) {}
};

struct C : Base {
  Base s1;
  int a = 0;
  Base s2;
  int b = 0;
  Base s3;
  int c = 0;
  Base s4;
  C();
  C(int);
  C(float);
  C(char);
  C(int*);
  C(float*);
  C(char*);
};

C::C() = default;
C::C(int)    : b(2), c(3) {}
C::C(float)  : a(1), c(3) {}
C::C(char)   : a(1), b(2) {}
C::C(int*)   : Base(-1), b(2), c(3) {}
C::C(float*) : Base(-1), a(1), c(3) {}
C::C(char*)  : Base(-1), a(1), b(2) {}

D::D() = default;
D::D(int)    : b(2), c(3) {a = {}; }
D::D(float)  : a(1), c(3) {b = {}; }
D::D(char)   : a(1), b(2) , c{} {}
D::D(int*)   : Base(-1), b(2), c(3) {a = {}; }
D::D(float*) : Base(-1), a(1), c(3) {b = {}; }
D::D(char*)  : Base(-1), a(1), b(2) , c{} {}
