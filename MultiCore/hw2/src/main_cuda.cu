#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <cmath>
#include <cstring>
#include "kernel.cu"
#include "utils.h"
using namespace std;

int main(int argc, char *argv[]) {
    int *in, *d_in;
    float *out, *d_out, *d_log;
    // 随机初始化矩阵
    int m = strtol(argv[1], NULL, 10);
    int n = strtol(argv[2], NULL, 10);
    Generate(&in, &out, m, n);
    // 线程块大小
    int b1 = strtol(argv[3], NULL, 10);
    int b2 = strtol(argv[4], NULL, 10);
    // CUDA优化版本号0-7
    int v = strtol(argv[5], NULL, 10);
    // 预处理
    float pre_log[26] = { 0.0, log2f(1.0), log2f(2.0), log2f(3.0), log2f(4.0), log2f(5.0),
                        log2f(6.0), log2f(7.0), log2f(8.0), log2f(9.0), log2f(10.0),
                        log2f(11.0), log2f(12.0), log2f(13.0), log2f(14.0), log2f(15.0),
                        log2f(16.0), log2f(17.0), log2f(18.0), log2f(19.0), log2f(20.0),
                        log2f(21.0), log2f(22.0), log2f(23.0), log2f(24.0), log2f(25.0)};
    // 显存分配
    CHECK(cudaMalloc((void**)&d_in, m * n * sizeof(int)));
    CHECK(cudaMalloc((void**)&d_out, m * n * sizeof(float)));
    CHECK(cudaMalloc((void**)&d_log, sizeof(pre_log)));
    // 数据拷贝
    CHECK(cudaMemcpy((void*)d_in, (void*)in, m * n * sizeof(int), cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy((void*)d_log, (void*)pre_log, sizeof(pre_log), cudaMemcpyHostToDevice));
    CHECK(cudaMemcpyToSymbol(const_log, (const float*)pre_log, sizeof(pre_log)));
    CHECK(cudaBindTexture(0, texture_log, d_log, sizeof(pre_log)));
    // blockSize和gridSize
    dim3 blockSize(b1, b2);
    dim3 gridSize(ceil((float) n / blockSize.x),
                  ceil((float) m / blockSize.y));
    // 记录时间
    cudaEvent_t t1, t2;
    cudaEventCreate(&t1);
    cudaEventCreate(&t2);
    // 调用核函数
    switch (v) {
        case 0:
            printf("Baseline: \n");
            cudaEventRecord(t1, 0);
            v0_baseline <<<gridSize, blockSize>>> (d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        case 1:
            printf("Unsigned Char\n");
            cudaEventRecord(t1, 0);
            v1_char <<<gridSize, blockSize>>> (d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        case 2:
            printf("Log Table in Register: \n");
            cudaEventRecord(t1, 0);
            v2_registerTable <<<gridSize, blockSize>>> (d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        case 3:
            printf("Log Table in Global Memory: \n");
            cudaEventRecord(t1, 0);
            v3_globalTable <<<gridSize, blockSize>>> (d_in, d_out, m, n, d_log);
            cudaEventRecord(t2, 0);
            break;
        case 4:
            printf("Log Table in Texture Memory: \n");
            cudaEventRecord(t1, 0);
            v4_textureTable <<<gridSize, blockSize>>> (d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        case 5:
            printf("Log Table in Constant Memory: \n");
            cudaEventRecord(t1, 0);
            v5_constTable <<<gridSize, blockSize>>> (d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        case 6:
            printf("Log Table in Shared Memory: \n");
            cudaEventRecord(t1, 0);
            v6_sharedTable <<<gridSize, blockSize>> >(d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        case 7:
            printf("Optimal: \n");
            cudaEventRecord(t1, 0);
            v7_optimal <<<gridSize, blockSize, b1 * b2 * 16 * sizeof(unsigned char)>>> (d_in, d_out, m, n);
            cudaEventRecord(t2, 0);
            break;
        default:
            cudaEventRecord(t1, 0);
            cudaEventRecord(t2, 0);
            break;
    }
    // 输出运行时间
    cudaEventSynchronize(t1);
    cudaEventSynchronize(t2);
    float t;
    cudaEventElapsedTime(&t, t1, t2);
    printf("Time cost (CUDA): %.3f ms\n", t);
    cudaEventDestroy(t1);
    cudaEventDestroy(t2);
    // 拷贝回host并释放显存
    CHECK(cudaUnbindTexture(texture_log));
    CHECK(cudaMemcpy((void*)out, (void*)d_out, m * n * sizeof(float), cudaMemcpyDeviceToHost));
    CHECK(cudaFree(d_in));
    CHECK(cudaFree(d_out));
    CHECK(cudaFree(d_log));
    // 检验正确性
    Evaluate(in, out, m, n);
    return 0;
}