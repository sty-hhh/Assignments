// Consider a simple loop that calls a function `dummy` containing a programmable delay （ sleep） . 
// All invocations of the function are independent of the others. Partition this loop across four threads 
// using `static`, `dynamic`, and `guided` scheduling. Use different parameters for static and guided scheduling. 
// Document the result of this experiment as the delay within the dummy function becomes large.  

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
            schedule(guided,10000)
        for (i = 0; i < 100000; ++i)
            dummy();
    }
    GET_TIME(end);
    printf("Run time: %e\n", (end-start)/100);
}
