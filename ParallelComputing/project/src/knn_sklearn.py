import numpy as np
import time
import random
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier

# MNIST手写数字数据集（28*28）
K = 10              # K值
sample_ratio = 1    # 选取数据集的采样率
split_ratio = 0.2   # 验证集比率

if __name__ == "__main__":
    data = np.genfromtxt("data.csv", delimiter=',', dtype=np.uint8)
    data = data[1:]         # 跳过第一行
    total = int(len(data)*sample_ratio)
    data = data[:total]
    valid_num = int(split_ratio * total)
    train_num = total - valid_num

    indexes = np.array(range(total))
    random.Random(0).shuffle(indexes)
    train_set = np.array([data[train] for train in indexes[:train_num]])
    valid_set = np.array([data[valid] for valid in indexes[train_num:]])

    train_data = train_set[:, 1:]
    train_labels = np.array([train[0] for train in train_set])
    valid_data = valid_set[:, 1:]
    valid_labels = np.array([valid[0] for valid in valid_set])

    neigh = KNeighborsClassifier(n_neighbors=10)
    
    start = time.time()
    neigh.fit(train_data, train_labels)
    prediction = neigh.predict(valid_data)
    end = time.time()

    print(end-start)
    print(accuracy_score(valid_labels, prediction))




