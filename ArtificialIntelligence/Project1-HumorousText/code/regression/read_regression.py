#encoding=UTF-8
import pandas as pd

# 读取文件
def read_file(filepath):
    df = pd.read_csv(filepath).values
    data_set = []
    rating_set = []
    for line in df:
        if line[2]==1:
            data_set.append(line[1])
            rating_set.append(line[3])
    return data_set, rating_set

# 读取测试集的序号和数据
def read_testfile(filepath):
    df = pd.read_csv(filepath)
    id = list(df.values[:, 0])
    data_set = list(df.values[:, 1])
    return id, data_set

# 读取数据集
data_set, rating_set = read_file('code/data/train.csv')
test_id, test_data = read_testfile('code/data/test_regression.csv')
total = len(data_set)

# 划分数据集
train_data  = data_set[:total//10*7]
valid_data  = data_set[total//10*7:]
train_rating = rating_set[:total//10*7]
valid_rating = rating_set[total//10*7:]
# train_data = data_set
# train_rating = rating_set