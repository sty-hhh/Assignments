import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 读取文件
def read_file(filename):
    df = pd.read_csv(filename, header = None)
    data_set = np.array(df.values)
    for i in range(len(data_set)):
        if data_set[i][-1] == 0.0:
            data_set[i][-1] = -1.0  # 将标签中的0改为-1
    return data_set

# 感知机算法
def PLA(train_set, epoches, LR):
    w = np.zeros(len(train_set[0])-1)
    b = 0
    for _ in range(epoches):
        flag = True
        for data in train_set:
            x = data[:-1]
            y = np.dot(x, w) + b
            if np.sign(y) != data[-1]:
                flag = False
                w += LR * data[-1] * x
                b += LR * data[-1]
                break
        if flag == True:    # 没有分错，直接跳出循环
            break
    return w,b

# 计算准确率
def cal_accuracy(valid_set, w, b):
    total = len(valid_set)
    cnt = 0
    for data in valid_set:
        x = data[:-1]
        y = np.dot(x, w) + b
        if np.sign(y) == data[-1] or y == 0:
            cnt += 1
    return cnt / total

if __name__ ==  '__main__':
    data_set = read_file('train.csv')
    total = len(data_set)
    # 训练集和验证集73开
    train_set = data_set[:total//10*7, :]
    valid_set = data_set[total//10*7:, :]
    LR = 0.01

    x = []
    y = []
    for i in range(1, 100, 2):
        w, b = PLA(train_set, i, LR)
        accuracy = cal_accuracy(valid_set, w, b)
        print("迭代次数：%s，准确率：%s" % (i, accuracy))
        x.append(i)
        y.append(accuracy)
    plt.plot(x, y)
    plt.grid(True)
    plt.xlabel('epoches')
    plt.ylabel('accuracy')
    plt.title('LR=%s PLA' % LR)
    plt.show()
    