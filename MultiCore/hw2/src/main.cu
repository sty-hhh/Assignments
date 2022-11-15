#include <stdio.h>
#include <stdlib.h>
#include "config.h"

//**************************************************************************
#include <cmath>
#include <iostream>
using namespace std;
__constant__ float const_log[26];
texture<float, 1> texture_log;

// Baseline
__global__ void v0_baseline(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    int cnt[16] = {0}, count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k]) 
                ans -= (float)cnt[k] *  (1.0 / count) * log2f((float)cnt[k]/count);
        out[idy*width+idx] = ans;
    }
}

// 计数器cnt用unsigned char代替int
__global__ void v1_char(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    unsigned char cnt[16] = {0}, count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k])
                ans -= (float)cnt[k] *  (1.0 / count) * log2f((float)cnt[k]/count);
        out[idy*width+idx] = ans;
    }
}

// 预处理对数表至寄存器
__global__ void v2_registerTable(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    unsigned char cnt[16] = {0}, count = 0;
    const float pre_log[26] = { 0.0, log2f(1.0), log2f(2.0), log2f(3.0), log2f(4.0), log2f(5.0),
                                log2f(6.0), log2f(7.0), log2f(8.0), log2f(9.0), log2f(10.0),
                                log2f(11.0), log2f(12.0), log2f(13.0), log2f(14.0), log2f(15.0),
                                log2f(16.0), log2f(17.0), log2f(18.0), log2f(19.0), log2f(20.0),
                                log2f(21.0), log2f(22.0), log2f(23.0), log2f(24.0), log2f(25.0)};
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k])
                ans -= (float)cnt[k] *  (1.0 / count) * (pre_log[cnt[k]]-pre_log[count]);
        out[idy*width+idx] = ans;
    }
}

// 预处理对数表至全局内存
__global__ void v3_globalTable(int *in, float *out, int height, int width, float *global_log) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    unsigned char cnt[16] = {0}, count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k])
                ans -= (float)cnt[k] *  (1.0 / count) * (global_log[cnt[k]]-global_log[count]);
        out[idy*width+idx] = ans;
    }
}

// 预处理对数表至纹理内存
__global__ void v4_textureTable(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    unsigned char cnt[16] = {0}, count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k])
                ans -= (float)cnt[k] *  (1.0 / count) * (tex1Dfetch(texture_log, cnt[k])-tex1Dfetch(texture_log, count));
        out[idy*width+idx] = ans;
    }
}

// 预处理对数表至常量内存
__global__ void v5_constTable(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    unsigned char cnt[16] = {0}, count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k])
                ans -= (float)cnt[k] *  (1.0 / count) * (const_log[cnt[k]]-const_log[count]);
        out[idy*width+idx] = ans;
    }
}

// 预处理对数表至共享内存
__global__ void v6_sharedTable(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    int tid = threadIdx.y * blockDim.x + threadIdx.x;
    __shared__ float shared_log[26];
    if (tid != 0 && tid < 26)
        shared_log[tid] = log2f((float)tid);
    __syncthreads();
    unsigned char cnt[16] = {0}, count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k)
            if (cnt[k])
                ans -= (float)cnt[k] *  (1.0 / count) * (shared_log[cnt[k]]-shared_log[count]);
        out[idy*width+idx] = ans;
    }
}

// 最佳优化版本
__global__ void v7_optimal(int *in, float *out, int height, int width) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const int idy = blockIdx.y * blockDim.y + threadIdx.y;
    int tid = threadIdx.y * blockDim.x + threadIdx.x;
    extern __shared__ unsigned char cnt[][16];
    memset(cnt + tid, 0, 16 * sizeof(unsigned char));
    __syncthreads();
    unsigned char count = 0;
    if (idy < height && idx < width) {
        for (int dy = -2; dy <= 2; ++dy)
            for (int dx = -2; dx <= 2; ++dx) {
                const int x = idx + dx, y = idy + dy;
                if (y >= 0 && y < height && x >= 0 && x < width) {
                    ++cnt[tid][in[y*width+x]];
                    ++count;
                }
            }
        float ans = 0;
        for (int k = 0; k < 16; ++k) 
            ans -= cnt[tid][k] ? cnt[tid][k] * (1.0 / count) * (const_log[cnt[tid][k]]-const_log[count]) : 0;
        out[idy*width+idx] = ans;
    }
}
//**************************************************************************

int main(int argc, char* argv[]) {
    if (argc == 3) {
        inputPath = argv[1];
        outputPath = argv[2];
    }

    // Open the input file
    FILE *stream = fopen(inputPath, "rb");
    if (stream == NULL) {
        printf("failed to open the data file %s\n", inputPath);
        return -1;
    }

    // Open a stream to write out results in text
    FILE *outStream = fopen(outputPath, "wb");
    if (outStream == NULL) {
        printf("failed to open the output file %s\n", outputPath);
        return -1;
    }

    // Read in and process the input matrix one-by-one
    int width, height, size;
    int *input;
    float *result;
    loadMatrix(stream, &width, &height, &input);
    size = width * height;
    result = (float*)malloc(sizeof(float) * size);

    //**************************************************************************
    int *d_in;
    float *d_out, *d_log;
    // 预处理
    float pre_log[26] = { 0.0, log2f(1.0), log2f(2.0), log2f(3.0), log2f(4.0), log2f(5.0),
                        log2f(6.0), log2f(7.0), log2f(8.0), log2f(9.0), log2f(10.0),
                        log2f(11.0), log2f(12.0), log2f(13.0), log2f(14.0), log2f(15.0),
                        log2f(16.0), log2f(17.0), log2f(18.0), log2f(19.0), log2f(20.0),
                        log2f(21.0), log2f(22.0), log2f(23.0), log2f(24.0), log2f(25.0)};
    // 显存分配
    CHECK(cudaMalloc((void**)&d_in, size * sizeof(int)));
    CHECK(cudaMalloc((void**)&d_out, size * sizeof(float)));
    CHECK(cudaMalloc((void**)&d_log, sizeof(pre_log)));
    // 数据拷贝
    CHECK(cudaMemcpy((void*)d_in, (void*)input, size * sizeof(int), cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy((void*)d_log, (void*)pre_log, sizeof(pre_log), cudaMemcpyHostToDevice));
    CHECK(cudaMemcpyToSymbol(const_log, (const float*)pre_log, sizeof(pre_log)));
    CHECK(cudaBindTexture(0, texture_log, d_log, sizeof(pre_log)));
    // blockSize和gridSize
    dim3 blockSize(8, 8);
    dim3 gridSize(divup(width, blockSize.x), divup(height, blockSize.y));
    // 记录时间
    long st, et;
    st = getTime();
    // 调用核函数
    int v = 7;
    switch (v) {
        case 0:
            printf("Baseline: \n");
            v0_baseline <<<gridSize, blockSize>>> (d_in, d_out, height, width);
            break;
        case 1:
            printf("Unsigned Char\n");
            v1_char <<<gridSize, blockSize>>> (d_in, d_out, height, width);
            break;
        case 2:
            printf("Log Table in Register: \n");
            v2_registerTable <<<gridSize, blockSize>>> (d_in, d_out, height, width);
            break;
        case 3:
            printf("Log Table in Global Memory: \n");
            v3_globalTable <<<gridSize, blockSize>>> (d_in, d_out, height, width, d_log);
            break;
        case 4:
            printf("Log Table in Texture Memory: \n");
            v4_textureTable <<<gridSize, blockSize>>> (d_in, d_out, height, width);
            break;
        case 5:
            printf("Log Table in Constant Memory: \n");
            v5_constTable <<<gridSize, blockSize>>> (d_in, d_out, height, width);
            break;
        case 6:
            printf("Log Table in Shared Memory: \n");
            v6_sharedTable <<<gridSize, blockSize>> >(d_in, d_out, height, width);
            break;
        case 7:
            printf("Optimal: \n");
            v7_optimal <<<gridSize, blockSize, 16 * 16 * 16 * sizeof(unsigned char)>>> (d_in, d_out, height, width);
            break;
        default:
            break;
    }
    // 输出运行时间
    et = getTime();
    printf("Time cost (CUDA): %.3f ms\n", et-st);
    // 拷贝回host并释放显存
    CHECK(cudaUnbindTexture(texture_log));
    CHECK(cudaMemcpy((void*)result, (void*)d_out, size * sizeof(float), cudaMemcpyDeviceToHost));
    CHECK(cudaFree(d_in));
    CHECK(cudaFree(d_out));
    CHECK(cudaFree(d_log));
    //**************************************************************************
       
    saveMatrix(outStream, &width, &height, &result);

    // De-allocate the input and the result
    free(input);
    input = NULL;
    free(result);
    result = NULL;
    
    // Close the stream
    fclose(stream);
    fclose(outStream);
    return 0;
}