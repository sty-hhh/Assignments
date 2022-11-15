import math
import pandas as pd
import numpy as np
import csv

# 读取文件
def read_file(file_name):
    # 从file_name读取
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        first = next(reader)    # 跳过第一行
        data = []
        labels = []
        # 如果是train_set或validation_set，需要读取文本内容和情感
        if file_name == 'train_set.csv' or file_name == 'validation_set.csv':
            for line in reader:
                data.append(line[0])     # train_set和validation_set的0列是文本内容
                labels.append(line[1])   # train_set和validation_set的1列是情感
            return data, labels
        # 如果是test_set，只需要读取文本内容
        else:
            for line in reader:
                data.append(line[1])     # test_data的1列是文本内容，0列是索引！
            return data

# 构建词表
def count_words(train_data):
    word_list = []
    word_set = set()
    for line in train_data:             # 训练集
        words =  line.split(' ')        # 将每一行用空格划分为多个单词
        for word in words:
            if word not in word_set:    # 用集合加速查找
                word_list.append(word)  # 如果单词不在词表中，则将单词加入词表
                word_set.add(word)
    return word_list

# 计算TF矩阵，求出TF矩阵的一行
def TF(words):
    tf = {}
    num = len(words)    # 计算一行中的单词个数
    for word in words:
        tf[word] = (tf.get(word, 0)*num+1)/num  # 按照公式计算TF
    return tf

# 计算IDF向量
def IDF(data, word_list):
    total = len(data)
    idf = []
    for word in word_list:  # 遍历词表中的每个词
        count = 0
        for sentence in data:
            words =  sentence.split(' ')    # 将每一行用空格划分为多个单词
            if word in words: 
                count += 1  # 如果该单词在这一行中，计数器count加上1
        idf.append(math.log(total/(count+1)))   # 利用公式计算
    return idf

# 计算TF-IDF矩阵
def TFIDF(data, word_list):
    idf = IDF(data, word_list)      # 计算idf的值
    tfidf = []
    for sentence in data:
        words = sentence.split(' ')
        tf = TF(words)              # 计算每一行的tf的值
        line = []
        index = 0
        for index, word in enumerate(word_list):
            x = tf.get(word, 0)*idf[index]  # 利用公式计算tf-idf
            line.append(x)                  # 在该行中添加一个值
        tfidf.append(line)          # tfidf矩阵添加一行
    tfidf = np.array(tfidf)
    return tfidf

# 构造onehot矩阵
def onehot(data, word_list):
    # onehot矩阵的宽是文本内容data的行数，长是词表word_list中word的个数
    onehot_matrix = np.zeros(shape=(len(data), len(word_list)))
    # 遍历word_list的每个单词，i是word的索引
    for i,word in enumerate(word_list):
        # 遍历文本内容data的每一行，index是line的索引
        for index,line in enumerate(data):
            words = line.split(' ')     # 将每一行用空格划分为多个单词
            if word in words:
                onehot_matrix[index][i] = 1     # onehot矩阵对应位置的值设为1
    return onehot_matrix

# 计算Lp距离
def cal_distance(train_matrix, line, p=2):
    # train_matrixs是整个训练集的矩阵
    # line是测试集矩阵的某一行
    # p是Lp距离中的p值，默认p=2欧氏距离
    line = line.reshape(1, -1) # 将line从列向量转为行向量
    lines = np.repeat(line, train_matrix.shape[0], axis=0)   # 将行向量扩展成矩阵
    # Lp距离
    temp = np.abs(lines - train_matrix)     # 求出矩阵相减后的绝对值
    distances = np.sum(temp**p, axis=1)**(1/p)  # 行内求和，和为列向量
    return distances

# 利用KNN处理分类问题
def KNN_predict(train_matrix, matrix, k, train_labels):
    # train_matrix是训练集的矩阵
    # matrix是验证集或测试集的矩阵
    # k是超参数
    # train_labels是训练集的情感标签

    # 构造一个共有matrix的行数的个数的list
    result = [0 for i in range(matrix.shape[0])]    
    # 遍历验证集/测试集矩阵的每一行
    for index in range(matrix.shape[0]):      # 按下标访问
        line = matrix[index]
        # 求出验证集或测试集矩阵中每一行与整个训练集矩阵的距离
        distances = cal_distance(train_matrix, line, 1)    # 默认欧氏距离p=2
        sort_index = np.argsort(distances)    # 从小到大排序，返回原始下标
        
        # 对距离最小的k组情感标签投票
        dict1 = {}
        i = 0
        while i < k:
            if train_labels[sort_index[i]] not in dict1:
                dict1[train_labels[sort_index[i]]] = 1      # 不在字典中设为1
            else:
                dict1[train_labels[sort_index[i]]] += 1     # 在字典中增加1
            i += 1
        # 找出字典中值最大对应的键
        result[index] = max(dict1, key=lambda x: dict1[x])   
    return result   # 返回预测的情感标签集合

# 从验证集中计算模型的准确率
def cal_accuracy(real, predict):
    # predict是预测的标签
    # real是真实的标签
    total = len(real)
    count = 0
    for i in range(total):
        if real[i] == predict[i]:
            count += 1      # 如果预测正确，计数器count加1
    return count/total      # 返回准确率

# 主函数
if __name__ ==  '__main__':
    # 读取文本内容和标签
    train_data, train_labels = read_file("train_set.csv")
    valid_data, valid_labels = read_file("validation_set.csv")
    test_data = read_file("test_set.csv")


    # 构建词表
    word_list = count_words(train_data)

    # # 构建训练集、验证集、测试集的onehot矩阵
    # train_matrix = onehot(train_data, word_list)
    # valid_matrix = onehot(valid_data, word_list)
    # test_matrix = onehot(test_data, word_list)

    # 构建训练集、验证集、测试集的tfidf矩阵
    train_matrix = TFIDF(train_data, word_list)
    valid_matrix = TFIDF(valid_data, word_list)
    test_matrix = TFIDF(test_data, word_list)

    # 训练模型，保存准确率最高的k值
    k_best = 1
    accuracy_best = 0
    k = 1
    while k <= 20:
        # 在验证集上预测情感标签
        valid_predict = KNN_predict(train_matrix, valid_matrix, k, train_labels)
        # 计算准确率
        accuracy = cal_accuracy(valid_labels, valid_predict)
        print('k = ', k, ', accuracy = ', accuracy)
        # 如果准确率最高，则保存k值
        if accuracy > accuracy_best:
            k_best = k
            accuracy_best = accuracy
        k += 1
    print('The best k is', k_best)                       # 输出最佳k值
    print('The highest accuracy is', accuracy_best)      # 输出最高的accuracy值

    # 在测试集上预测情感标签，运用pandas输出csv文件
    test_predict = KNN_predict(train_matrix, test_matrix, k_best, train_labels)
    test_output = pd.DataFrame({'Words (split by space)': test_data, 'label': test_predict})
    test_output.to_csv('19335174_ShiTianyu_KNN_classification.csv.csv', index=None, encoding='utf8')    
