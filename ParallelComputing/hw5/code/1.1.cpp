#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <omp.h>
#include <unistd.h>
#include <sys/time.h>
using namespace std;

#define GET_TIME(now) { \
    struct timeval t; \
    gettimeofday(&t, NULL); \
    now = t.tv_sec + t.tv_usec/1000000.0; \
}

void dummy(){
    for (int j = 0; j < 10; ++j);
}

int main() {
    double start, end;
    int i, k = 100;
    GET_TIME(start);
    while (k--) {
#       pragma omp parallel for num_threads(4) \
            schedule(static,25000)
        for (i = 0; i < 100000; ++i)
            dummy();
    }
    GET_TIME(end);
    printf("Run time: %e\n", (end-start)/100);
}
