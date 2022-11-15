#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <cmath>
#include <omp.h>
using namespace std;

// 随机初始化两个 m*n 大小的矩阵
void Generate(float **a, float **b, float **c, int m, int n) {
    *a = new float[m*n], *b = new float [m*n], *c = new float [m*n];
    for (int i = 0; i < m; ++i) 
        for (int j = 0; j < n; ++j) {
            (*a)[i*n+j] = 10.0 * rand()/(RAND_MAX+1.0);
            (*b)[i*n+j] = 10.0 * rand()/(RAND_MAX+1.0);
        }
}
// 检验矩阵加法计算结果
void Evaluate(float *a, float *b, float *c, int m, int n) {
    for (int i = 0; i < m; ++i) 
        for (int j = 0; j < n; ++j) 
            if ((fabs(a[i*n+j] + b[i*n+j]- c[i*n+j]) / c[i*n+j]) > 1e-4) {
                printf("Computation Error In %d Row %d Col!\n", i, j);
                return;
            }
    printf("Computation Correct!\n");
}

int main(int argc, char *argv[]) {
    float *a, *b, *c;
    int m = strtol(argv[1], NULL, 10);
    int n = strtol(argv[2], NULL, 10);
    // 随机初始化矩阵
    Generate(&a, &b, &c, m, n);
    // 线程数
    int thread_num = strtol(argv[3], NULL, 10);
    // 开始时间
    double start = omp_get_wtime();
    // 矩阵加法
#   pragma omp parallel for num_threads(thread_num)
        for (int i = 0; i < m; ++i)
            for (int j = 0; j < n; ++j) {
                int id = i * n + j;
                c[id] = a[id] + b[id];
            }
    // 输出运行时间
    double end = omp_get_wtime( );
    printf("Time cost(OpenMP): %.3f ms\n", (end - start) * 1000);
    // 检验正确性
    Evaluate(a, b, c, m, n);
    return 0;
}
