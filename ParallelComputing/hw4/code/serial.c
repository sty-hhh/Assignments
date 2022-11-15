#include<stdio.h>
#include<stdlib.h>
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
double start, stop;

int main(){
    for (int i = 0; i < col; ++i)
        vector[i] = rand() % 10;
    for (int i = 0; i < row; ++i)
        for(int j = 0; j < col; ++j)
            matrix[i][j] = rand() % 10;
    GET_TIME(start);
    for (int i = 0;i < row;i++)
        for(int j = 0;j < col; ++j)
            res[i] += matrix[i][j] * vector[j];
    GET_TIME(stop);
    printf("Run time: %e\n", stop-start);
    return 0;
}
