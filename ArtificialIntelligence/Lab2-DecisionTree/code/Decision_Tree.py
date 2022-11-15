import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

# 读取文件
def read_file(filename):
    df = pd.read_csv(filename)
    data_set = list(df.values)
    attribute_set = list(df.columns.values)
    return data_set, attribute_set

# 构成各种属性对应可能取值的字典
def get_dictionary(data_set, attribute_set):
    # data_set：数据集
    # attribute_set: 属性名称集合
    # 返回属性字典：key为attribute_set中的下标，value为对应属性可能的取值
    dic = {}
    total = len(attribute_set) - 1  # 不算最后的label
    for i in range(total):
        temp = set()
        for line in data_set:
            temp.add(line[i])
        dic[i] = temp
    return dic

# 划分数据集
def split_dataset(data_set, attribute_index, value):
    # data_set：数据集
    # attribute_index：所选属性的下标
    # value：属性的具体值
    sub_set = []
    for line in data_set:
        if line[attribute_index] == value:
            sub_set.append(line)
    return sub_set

# 计算经验熵
def cal_entropy(data_set, attribute_index):
    # data_set：数据集
    # attribute_index：所选属性的下标
    cnt = {}  # 存储属性的取值及其数量
    for line in data_set:
        value = line[attribute_index]
        cnt[value] = cnt.get(value, 0) + 1  # 计算属性的每种取值的个数
    entropy = 0.0
    for count in cnt.values():
        p = float(count) / len(data_set)  
        if p != 0:
            entropy -= p * math.log2(p)     # 用经验熵公式计算
    return entropy

# 计算信息增益
def cal_gain(data_set, dic, attribute_index, empirical_entropy):
    # data_set：数据集
    # dic: 属性字典，对应每种属性的取值
    # attribute_index：所选属性的下标
    # empirical_entropy：经验熵
    total = len(data_set)
    conditional_entropy = 0.0
    for value in dic[attribute_index]:  # 遍历这个属性对应的取值
        sub_set = split_dataset(data_set, attribute_index, value)   # 获得对应属性的子数据集
        p = len(sub_set) / total
        conditional_entropy += p * cal_entropy(sub_set, -1)  # 计算条件熵
    return empirical_entropy - conditional_entropy

# 计算基尼系数
def cal_gini(data_set, attribute_index):
    # data_set：数据集
    # attribute_index：所选属性的下标
    attribute_count = {}    # 所选属性的每种取值的数量
    attribute_label = {}    # 所选属性的每种取值对应的label数量
    total = len(data_set)
    for line in data_set:
        value = line[attribute_index]
        attribute_count[value] = attribute_count.get(value, 0) + 1
        attribute_label[value] = attribute_label.get(value, {})     # get默认返回空
        if line[-1] not in attribute_label[value]:
            attribute_label[value][line[-1]] = 0    # 将对应的label的次数赋为0
        attribute_label[value][line[-1]] += 1
    gini = 0.0
    for value in attribute_count.keys():
        size = attribute_count[value]   # 当前属性取value值的数量
        temp = 1
        for x in attribute_label[value].values():
            temp -= np.square(x / size)
        gini += size / total * temp     # 计算基尼系数
    return gini

# 选择最优属性
def choose_attribute(data_set, dic, left_attribute, strategy):
    # data_set: 数据集
    # dic: 属性字典，对应每种属性的取值
    # left_attribute: 当前剩下的的属性集合，存的是属性在dic中对应的下标
    # strategy: 特征选择的方法
    if strategy == "ID3":
        gain_list = []
        for attribute_index in left_attribute:   # 遍历每种属性的下标
            empirical_entropy = cal_entropy(data_set, -1)  # 经验熵
            gain = cal_gain(data_set, dic, attribute_index, empirical_entropy)
            gain_list.append(gain)
        max_index = np.argmax(gain_list)  # 信息增益最大的下标
        return left_attribute[max_index] 
    elif strategy == "C4.5":
        gainRatio_list = []
        for attribute_index in left_attribute:   # 遍历每种属性的下标
            empirical_entropy = cal_entropy(data_set, -1)  # 经验熵
            gain = cal_gain(data_set, dic, attribute_index, empirical_entropy)
            SplitInfo = cal_entropy(data_set, attribute_index)    # 计算特征的信息熵
            if SplitInfo == 0:     # 说明这个属性对决策没贡献
                continue
            gainRatio_list.append(gain/SplitInfo)
        max_index = np.argmax(gainRatio_list)  # 信息增益率最大的下标
        return left_attribute[max_index]
    elif strategy == "CART":
        gini_list = []
        for i in left_attribute:
            gini = cal_gini(data_set, i)    # 计算基尼系数
            gini_list.append(gini)
        min_index = np.argmin(gini_list)    # 基尼系数最小的下标
        return left_attribute[min_index]

# 构造决策树节点
class TreeNode(object):
    # 初始化类实例
    def __init__(self, label=None, attribute=None, branch=None):
        self.attribute = attribute  # 节点的属性标签
        self.label = label  # 保存当前分支的label
        self.branch = branch    # 树的分支

# 构建决策树
def create_tree(data_set, dic, left_attribute, parent_label, strategy):
    # data_set: 数据集
    # dic: 属性字典，对应每种属性的取值
    # left_attribute: 当前剩下的的属性集合，存的是属性在dic中对应的下标
    # parent_label: 父节点的label
    # strategy: 特征选择的方法
    label_list = [line[-1] for line in data_set]
    # 边界条件
    if len(data_set) == 0:  # data_set为空集，取父节点出现最多的label
        return TreeNode(label=parent_label)
    if len(left_attribute) == 0:    # 没有属性可选时，即left_atttribute为空时，找出众数标签
        label = max(label_list, key=label_list.count)
        return TreeNode(label=label)
    if label_list.count(label_list[0]) == len(label_list):  # data_set里的样本都取同一label
        return TreeNode(label=label_list[0])  
    # 选择出最好的属性，返回对应属性的下标
    best_attribute = choose_attribute(data_set, dic, left_attribute, strategy)
    left_attribute.remove(best_attribute)   # 去除最好的属性
    branch = {}
    parent_label = max(label_list, key=label_list.count)     # 将父节点出现最多的label传给子树
    for value in dic[best_attribute]:     # 用最好的属性划分data_set，构建子树
        sub_set = split_dataset(data_set, best_attribute, value)
        branch[value] = create_tree(sub_set, dic, left_attribute[:], parent_label, strategy)
    return TreeNode(label=parent_label, attribute=best_attribute, branch=branch)

# 计算验证集的准确率
def cal_accuracy(valid_set, root):
    cnt = 0
    for line in valid_set:
        cur = root
        while cur.branch is not None:
            cur = cur.branch[line[cur.attribute]]   # 直到叶子节点
        if cur.label == line[-1]:
            cnt += 1
    return cnt/len(valid_set)

# k折交叉验证
def k_fold(data_set, k, index):
    total = len(data_set)
    start = index * total // k 
    end = start + total // k 
    train_set = data_set[:start] + data_set[end:]
    valid_set = data_set[start:end]
    return train_set, valid_set

# 验证集预测
def validation(data_set, attribute_set, dic, strategy):
    x = []
    y = []
    k_best = 0
    accuracy_best = 0
    print(strategy, '方法')
    for k in range(2, 10):
        temp = 0
        for i in range(k):  # 对不同的验证集取均值作为一个k的结果
            train_set, valid_set = k_fold(data_set, k, i)
            left_attribute = list(range(0, len(attribute_set) - 1))
            root = create_tree(train_set, dic, left_attribute, -1, strategy)
            temp += cal_accuracy(valid_set, root)
        accuracy = temp / k
        print('用', k,'折交叉验证时，准确率为', accuracy)
        if accuracy > accuracy_best:
            k_best = k
            accuracy_best = accuracy
        x.append(k)
        y.append(accuracy)
    print('用', k_best,'折交叉验证时最佳，最高准确率为', accuracy_best)
    print()
    plt.plot(x, y, label=strategy)
    plt.grid(True)
    plt.xlabel('k')
    plt.ylabel('accuracy')
    plt.title(strategy)
    plt.legend()
    plt.show() 

# 测试集预测
def predict(test_set, root):
    test = []
    for line in test_set:
        cur = root
        while cur.branch is not None:
            cur = cur.branch[line[cur.attribute]]
        test.append(cur.label)
    return test

# 计算树的节点数
def cal(root):
    queue = []
    queue.append(root)
    res = 0
    while queue:
        size = len(queue)
        res += size
        for i in range(0, size):
            node = queue[0]
            queue.pop(0)
            if node.branch is not None:
                for value in dic[node.attribute]:
                    queue.append(node.branch[value])
    return res

# 主函数
if __name__ ==  '__main__':
    data_set, attribute_set = read_file('car_train_with_label.csv')
    test_set, test_attribute_set = read_file('car_test_without_label_1.csv')
    dic = get_dictionary(data_set, attribute_set)

    validation(data_set, attribute_set, dic, 'ID3')
    validation(data_set, attribute_set, dic, 'C4.5')
    validation(data_set, attribute_set, dic, 'CART')

    # strategy = 'CART'
    # left_attribute = list(range(0, len(attribute_set)-1))
    # root = create_tree(data_set, dic, left_attribute, -1, strategy)
    # test = predict(test_set, root)
    # print(test)

    # n = cal(root)
    # print(n)

    # accuracy = cal_accuracy(valid_set, root)
    # print('测试集准确率为', accuracy)

