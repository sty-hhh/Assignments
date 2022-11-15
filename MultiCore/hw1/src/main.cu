#include <stdio.h>
#include <stdlib.h>
#include "config.h"

//**************************************************************************
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
    float *input1, *input2, *result;
    loadMatrix(stream, &width, &height, &input1);
    loadMatrix(stream, &width, &height, &input2);
    size = width * height;
    result = (float*)malloc(sizeof(float) * size);

    //**************************************************************************
    // 显存分配
    float *da, *db, *dc;
    CHECK(cudaMalloc((void**)&da, size*sizeof(float)));
    CHECK(cudaMalloc((void**)&db, size*sizeof(float)));
    CHECK(cudaMalloc((void**)&dc, size*sizeof(float)));
    // 数据拷贝
    CHECK(cudaMemcpy((void*)da, (void*)input1, size*sizeof(float), cudaMemcpyHostToDevice));
    CHECK(cudaMemcpy((void*)db, (void*)input2, size*sizeof(float), cudaMemcpyHostToDevice));
    // 设置blockSize和gridSize
    int b1 = 32;         // blockSize一维
    int b2 = 32;         // blockSize二维（1代表一维块）
    int grid_dim = 2;    // grid维度
    int sz = 2;          // 每个线程计算的元素数（平方根）
    if (grid_dim == 1)  
        sz = sz * sz;
    dim3 blockSize(b1, b2);
    dim3 gridSize;
    // block一维, grid一维
    if (b2 == 1 && grid_dim == 1)  
        gridSize = dim3(divup(divup(size, sz), blockSize.x));
    // block一维，grid二维 或 block二维，grid二维
    else if (grid_dim == 2)  
        gridSize = dim3(divup(divup(width, sz), blockSize.x), divup(divup(height, sz), blockSize.y));

    long st, et;
    st = getTime();
    // 调用核函数
    if (grid_dim == 1)  
        MatrixMul_1d <<<gridSize, blockSize>>> (da, db, dc, height, width, sz);
    else    
        MatrixMul_2d <<<gridSize, blockSize>>> (da, db, dc, height, width, sz);
    et = getTime();
    printf("Time cost (CUDA): %.3f ms\n", (et - st) / 1e6);

    // 拷贝回host并释放显存
    CHECK(cudaMemcpy((void*)result, (void*)dc, size*sizeof(float), cudaMemcpyDeviceToHost));
    CHECK(cudaFree(da));
    CHECK(cudaFree(db));
    CHECK(cudaFree(dc));
    //**************************************************************************
       
    saveMatrix(outStream, &width, &height, &result);

    // De-allocate the nput and the result
    free(input1);
    free(input2);
    input1 = input2 = NULL;
    free(result);
    result = NULL;
    

    // Close the output stream
    fclose(outStream);
    return 0;
}