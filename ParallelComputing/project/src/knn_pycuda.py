import numpy as np
import random
import time
import pycuda.driver as drv
import pycuda.autoinit
from pycuda.compiler import SourceModule
from sklearn.metrics import accuracy_score

# MNIST手写数字数据集（28*28）
K = 10              # K值
sample_ratio = 1    # 选取数据集的采样率
split_ratio = 0.2   # 验证集比率  

# mod = SourceModule ("""
# #include <stdint.h>
# #include <math.h>
# __global__ void get_neighbor_dist(uint8_t* train, uint8_t* valid, uint32_t* dest, int offset, int train_num)
# {
#     int bid = blockIdx.x;
#     int x = threadIdx.x;
#     uint8_t *cur_item = valid + offset * 784;
#     __shared__ float dist_arr [784];

#     int difference = *(cur_item + x) - *(train + bid * 784 + x);
#     dist_arr[x] = difference * difference;
    
#     for (int stride = 392; stride > 0; stride /= 2) {
#         __syncthreads();
#         if (x < stride)
#             dist_arr[x] += dist_arr[x + stride];
#     }
#     if (x == 0) 
#         dest[offset * train_num + bid] = (int)sqrt(dist_arr[0]);
#     return;
# }
# """)

mod = SourceModule ("""
#include <stdint.h>
#include <math.h>
__global__ void get_neighbor_dist(uint8_t* train, uint8_t* valid, uint32_t* dest, int offset, int train_num)
{
    int bid = blockIdx.x;
    int x = threadIdx.x;
    uint8_t *cur_item = valid + offset * 784;
    __shared__ float dist_arr [832];
    if (x < 392) {
        int difference = *(cur_item + x) - *(train + bid * 784 + x);
        dist_arr[x] = difference * difference;
        difference = *(cur_item + 392 + x) - *(train + bid * 784 + 392 + x);
        dist_arr[x + 416] = difference * difference;
    }
    else {
        dist_arr[x] = 0;
        dist_arr[x + 416] = 0;
    }
    for (int stride = 416; stride > 0; stride /= 2) {
        __syncthreads();
        if (x < stride)
            dist_arr[x] += dist_arr[x + stride];
    }
    if (x == 0) 
        dest[offset * train_num + bid] = (int)sqrt(dist_arr[0]);
    return;
}
""")


def most_frequent(List):
    return max(set(List), key=List.count)


def GPU_init_memory(train_set, valid_data, valid_num, train_num):
    train_gpu = drv.mem_alloc(train_set.nbytes)
    drv.memcpy_htod(train_gpu, train_set)
    valid_gpu = drv.mem_alloc(valid_data.nbytes)
    drv.memcpy_htod(valid_gpu, valid_data)
    dest_gpu = drv.mem_alloc(valid_num * train_num * 4)  # uint32
    return train_gpu, valid_gpu, dest_gpu


def parallel_KNN(train_set, valid_data, valid_num, train_num, K):
    train_labels = np.array([item[0] for item in train_set])
    train_data = np.array([item[1:] for item in train_set])
    train_gpu, valid_gpu, dest_gpu = GPU_init_memory(train_data, valid_data, valid_num, train_num)
    func = mod.get_function("get_neighbor_dist")
    for i in range(valid_num):
        func(train_gpu, valid_gpu, dest_gpu, np.int32(i), np.int32(train_num), block=(416, 1, 1), grid=(train_num, 1, 1))

    results = np.empty([valid_num, train_num], dtype=np.uint32)
    drv.memcpy_dtoh(results, dest_gpu)

    prediction = np.empty((len(valid_set)), dtype='uint8')
    for i, item in enumerate(results):
        index_arr = np.argpartition(item, K)[:K]    # topK的label
        prediction[i] = most_frequent([train_labels[index] for index in index_arr])  # K个label中投票

    return prediction


if __name__ == "__main__":
    data = np.genfromtxt("data.csv", delimiter=',', dtype=np.uint8)
    data = data[1:]         # 跳过第一行
    total = int(len(data)*sample_ratio)
    data = data[:total]
    valid_num = int(split_ratio * total)
    train_num = total - valid_num

    indexes = np.array(range(total))
    random.Random(0).shuffle(indexes)
    train_set = [data[train] for train in indexes[:train_num]]
    valid_set = [data[valid] for valid in indexes[train_num:]]

    valid_labels = np.array([item[0] for item in valid_set])
    valid_data = np.array([item[1:] for item in valid_set])

    start = time.time()
    prediction = parallel_KNN(train_set, valid_data, valid_num, train_num, K)
    end = time.time()

    print(end-start)
    print(accuracy_score(valid_labels, prediction))
        