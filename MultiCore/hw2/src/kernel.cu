#include <cstdio>
#include <cmath>
#include "utils.h"

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


