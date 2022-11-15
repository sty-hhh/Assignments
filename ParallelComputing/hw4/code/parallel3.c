#include<stdio.h>
#include<stdlib.h>
#include<omp.h>
#include<string.h>
#include<sys/time.h>

#define row 1000
#define col 1000
#define GET_TIME(now) { \
    struct timeval t; \
    gettimeofday(&t, NULL); \
    now = t.tv_sec + t.tv_usec/1000000.0; \
}
int matrix[row][col];
int vector[row];
int res[row];
int thread_count, i, j, k;
double start, stop;

int main(int argc, char* argv[]) {
    if (argc == 2)
        thread_count = strtol(argv[1], NULL, 10);
    for (int i = 0; i < col; ++i)
        vector[i] = rand() % 10;
    for (int i = 0; i < row; ++i)
        for(int j = 0; j < col; ++j)
            matrix[i][j] = rand() % 10;

    /*static, chunk*/
    memset(res, 0, sizeof(res));
    GET_TIME(start);
#   pragma omp parallel for num_threads(thread_count) \
        default(none) private(i, j) shared(matrix, vector, res, thread_count) \
        schedule(static, 1000/thread_count)
    for (i = 0; i < row; ++i)
        for(j = 0; j < col; ++j)
            res[i] += matrix[i][j] * vector[j];
    GET_TIME(stop);
    printf("Run time: %e\n", stop-start);

    /*static, round-robin*/
    memset(res, 0, sizeof(res));
    GET_TIME(start);
#   pragma omp parallel for num_threads(thread_count) \
        default(none) private(i, j) shared(matrix, vector, res) \
        schedule(static, 1)
    for (i = 0; i < row; ++i)
        for(j = 0; j < col; ++j)
            res[i] += matrix[i][j] * vector[j];
    GET_TIME(stop);
    printf("Run time: %e\n", stop-start);

    return 0;
}