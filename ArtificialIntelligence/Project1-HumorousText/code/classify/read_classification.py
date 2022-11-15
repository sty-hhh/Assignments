#encoding=UTF-8
import pandas as pd

# 读取文件
def read_file(filepath):
    df = pd.read_csv(filepath)
    data_set = list(df.values[:, 1])
    label_set = list(df.values[:, 2])
    return data_set, label_set

# 读取测试集
def read_testfile(filepath):
    df = pd.read_csv(filepath)
    data_set = list(df.values[:, 1])
    return data_set

# 读取数据集
data_set, label_set = read_file('code/data/train.csv')
test_data = read_testfile('code/data/test_classification.csv')
total = len(data_set)

# 划分数据集
train_data  = data_set[:total//10*7]
valid_data  = data_set[total//10*7:]
train_labels = label_set[:total//10*7]
valid_labels = label_set[total//10*7:]