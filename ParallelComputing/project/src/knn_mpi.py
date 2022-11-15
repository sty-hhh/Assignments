import numpy as np
import time
import random
from sklearn.metrics import accuracy_score
from mpi4py import MPI

# MNIST手写数字数据集（28*28）
K = 10              # K值
sample_ratio = 1    # 选取数据集的采样率
split_ratio = 0.2   # 验证集比率

def most_frequent(List):
    return max(set(List), key=List.count)

def KNN(valid_set, train_set, K):
    dist_arr = np.array([np.linalg.norm(valid_set[1:] - other[1:]) for other in train_set]) # 欧氏距离
    index_arr = np.argpartition(dist_arr, K)[:K]
    return most_frequent([item[0] for item in [train_set[p] for p in index_arr]])

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if rank == 0:
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
        start_time = time.time()
    else:
        train_set = None
        valid_set = None
  
    train_set = comm.bcast(train_set, root=0)
    valid_set = comm.bcast(valid_set, root=0)

    local_start = rank * (len(valid_set) // size)
    local_end   = len(valid_set)-1 if rank==size-1 else local_start+(len(valid_set)//size)-1
    local_n = local_end - local_start + 1
    local_pred = np.empty((local_n), dtype='uint8')
    for i in range(local_start, local_end+1):
        local_pred[i-local_start] = KNN(valid_set[i], train_set, K)
    if rank != 0:
        comm.send(local_pred, dest=0)
    
    if rank == 0:
        prediction = np.empty((len(valid_set)), dtype='uint8')
        prediction[:local_n] = local_pred
        for i in range(1, size):
            data = comm.recv(source=i)
            start = i*(len(valid_set)//size)
            end = len(valid_set)-1 if i==size-1 else start+(len(valid_set)//size)-1
            prediction[start:end+1] = data
        end_time = time.time()
        print(end_time-start_time)
        print(accuracy_score([valid[0] for valid in valid_set], prediction))
