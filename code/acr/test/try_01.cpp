#include <cstdio>

int main(int argc, char** argv) {
    int x = 777;
    try {
        if (argc == 1) {
            throw "Divide-by-zero";
        }
        x = 12 / (argc - 1);
    } catch (...) {
        std::printf("Oh no!\n");
    }
    return 0;
}
