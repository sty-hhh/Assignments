#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <cmath>
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
// 一维加法
__global__ void MatrixMul_1d(float *a, float *b, float *c, int m, int n, int sz) {
    int id = (threadIdx.x + blockIdx.x * blockDim.x) * sz;
    for (int i = id; i < id + sz; ++i)
        if (i < m * n)  
            c[i] = a[i] + b[i];
}
// 二维加法
__global__ void MatrixMul_2d(float *a, float *b, float *c, int m, int n, int sz) {
    int idx = (threadIdx.x + blockIdx.x * blockDim.x) * sz;
    int idy = (threadIdx.y + blockIdx.y * blockDim.y) * sz;
    for (int y = idy; y < idy + sz; ++y) 
        for (int x = idx; x < idx + sz; ++x) 
            if (y < m && x < n) {
                int id = y * n + x;
                c[id] = a[id] + b[id];
            }    
}

int main(int argc, char *argv[]) {
    float *a, *b, *c, *da, *db, *dc, t;
    int m = strtol(argv[1], NULL, 10);
    int n = strtol(argv[2], NULL, 10);
    // 随机初始化矩阵
    Generate(&a, &b, &c, m, n);
    // 显存分配
    cudaMalloc((void**)&da, m*n*sizeof(float));
    cudaMalloc((void**)&db, m*n*sizeof(float));
    cudaMalloc((void**)&dc, m*n*sizeof(float));
    // 数据拷贝
    cudaMemcpy((void*)da, (void*)a, m*n*sizeof(float), cudaMemcpyHostToDevice);
    cudaMemcpy((void*)db, (void*)b, m*n*sizeof(float), cudaMemcpyHostToDevice);
    // 设置blockSize和gridSize
    int b1 = strtol(argv[3], NULL, 10);         // blockSize一维
    int b2 = strtol(argv[4], NULL, 10);         // blockSize二维（1代表一维块）
    int grid_dim = strtol(argv[5], NULL, 10);   // grid维度
    int sz = strtol(argv[6], NULL, 10);         
    if (grid_dim == 1)  
        sz = sz * sz;
    dim3 blockSize(b1, b2);
    dim3 gridSize;
    // block一维, grid一维
    if (b2 == 1 && grid_dim == 1)  
        gridSize = dim3(ceil(ceil((float)m*n/sz) / blockSize.x));
    // block一维，grid二维 或 block二维，grid二维
    else if (grid_dim == 2)  
        gridSize = dim3(ceil(ceil((float)n/sz) / blockSize.x), ceil(ceil((float)m/sz) / blockSize.y));
    // 记录时间
    cudaEvent_t t1, t2;
    cudaEventCreate(&t1);
    cudaEventCreate(&t2);
    cudaEventRecord(t1, 0);
    // 调用核函数
    if (grid_dim == 1)  
        MatrixMul_1d <<<gridSize, blockSize>>> (da, db, dc, m, n, sz);
    else    
        MatrixMul_2d <<<gridSize, blockSize>>> (da, db, dc, m, n, sz);
    // 输出运行时间
    cudaEventRecord(t2, 0);
    cudaEventSynchronize(t1);
    cudaEventSynchronize(t2);
    cudaEventElapsedTime(&t, t1, t2);
    printf("Time cost(CUDA): %.3f ms\n", t);
    cudaEventDestroy(t1);
    cudaEventDestroy(t2);
    // 拷贝回host并释放显存
    cudaMemcpy((void*)c, (void*)dc, m*n*sizeof(float), cudaMemcpyDeviceToHost);
    cudaFree(da);
    cudaFree(db);
    cudaFree(dc);
    // 检验正确性
    Evaluate(a, b, c, m, n);
    return 0;
}
