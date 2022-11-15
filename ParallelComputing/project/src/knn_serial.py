import numpy as np
import time
import random
from sklearn.metrics import accuracy_score

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

    prediction = np.empty((len(valid_set)), dtype='uint8')
    start = time.time()
    for i, valid in enumerate(valid_set):
        prediction[i] = KNN(valid, train_set, K)
    end = time.time()

    print(end-start)
    print(accuracy_score([valid[0] for valid in valid_set], prediction))

