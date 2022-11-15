import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 读取文件
def read_file(filename):
    df = pd.read_csv(filename, header = None)
    data_set = np.array(df.values)
    return data_set

# logistic函数
def pi(w, x):
    w = w.reshape((-1, 1))
    res = 1 / (1 + np.exp(-np.dot(x, w)))
    return res

# 逻辑回归算法
def logistic(train_set, epoches, LR):
    w = np.zeros(len(train_set[0]))
    h = np.ones(train_set.shape[0])
    # 给train_set末尾加一列1
    train_set = np.insert(train_set, train_set.shape[1]-1, values=h, axis=1)
    for _ in range(epoches):
        gradient = np.empty([]) # 损失函数的梯度
        x = train_set[:, :-1]   # 40个属性和'1'
        y = train_set[:, -1]    # 标签
        y = y.reshape((-1, 1))
        temp = y - pi(w, x)     # 用logistic函数计算
        for i in range(x.shape[1]-1):
            t = np.dot(x[:, i], temp)
            gradient = np.append(gradient, -t)
        w1 = w - LR * gradient
        d = np.linalg.norm(w1 - w)  # 求梯度变化的二范数（欧氏距离）
        if d <= 0.0001:     # 收敛则停止迭代
            break
        w = w1  # 更新参数
    return w

# 计算准确率
def cal_accuracy(valid_set, w):
    total = len(valid_set)
    cnt = 0
    h = np.ones(valid_set.shape[0])
    valid_set = np.insert(valid_set, valid_set.shape[1]-1, values=h, axis=1)
    for data in valid_set:
        x = data[:-1]
        y = pi(x, w)
        if (y >= 0.5 and data[-1] == 1) or (y < 0.5 and data[-1] == 0):
            cnt += 1
    return cnt / total

if __name__ ==  '__main__':
    data_set = read_file("train.csv")
    total = len(data_set)
    # 训练集和验证集73开
    train_set = data_set[:total//10*7, :]
    valid_set = data_set[total//10*7:, :]
    LR = 0.000001

    x = []
    y = []
    for i in range(1, 100, 2):
        w = logistic(train_set, i, LR)
        accuracy = cal_accuracy(valid_set, w)
        print("迭代次数：%s，准确率：%s" % (i, accuracy))
        x.append(i)
        y.append(accuracy)
    plt.plot(x, y)
    plt.grid(True)
    plt.xlabel('epoches')
    plt.ylabel('accuracy')
    plt.title('LR=%s LOGISTIC' % LR)
    plt.show()
