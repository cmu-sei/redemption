typedef int *INTPTR;

int main() {
	int x = 42;
	INTPTR p = &x;
	return *p;
}
