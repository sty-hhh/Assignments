#ifndef UTILS
#define UTILS

#include <cstdio>
#include <cmath>
#include <cstring>

#define CHECK(call)                                       \
    {                                                     \
        const cudaError_t error = call;                   \
        if (error != cudaSuccess)                         \
        {                                                 \
            printf("Error: %s:%d, ", __FILE__, __LINE__); \
            printf("code:%d, reason: %s \n",              \
                   error, cudaGetErrorString(error));     \
            exit(1);                                      \
        }                                                 \
    }
    
// 随机初始化 m*n 大小的矩阵
void Generate(int **in, float **out, int m, int n) {
    *in = new int[m*n], *out = new float [m*n];
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < n; ++j)
            (*in)[i*n+j] = rand() % 16;
}

// 检验计算结果
void Evaluate(int *in, float *out, int m, int n) {
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < n; ++j) {
            int cnt[16] = {0}, count = 0;
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = i + dx;
                if (x >= 0 && x < m) {
                    for (int dy = -2; dy <= 2; ++dy) {
                        const int y = j + dy;
                        if (y >= 0 && y < n) {
                            ++cnt[in[x*n+y]];
                            ++count;
                        }
                    }
                }
            }
            double ans = 0; 
            for (int k = 0; k < 16; ++k) 
                if (cnt[k]) 
                    ans -= (double)cnt[k] *  (1.0 / count) * log2f((float)cnt[k]/count);
            if (fabs(out[i*n+j] - ans) > 1e-5) {
                printf("Computation Error In %d Row %d Col!\n", i, j);
                return;
            }
        }
    printf("Computation Correct!\n");
}

#endif