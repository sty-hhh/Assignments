#encoding=UTF-8
import pandas as pd
import numpy as np
import random
import time
import math
from joblib import Parallel, delayed



# 决策树
class Tree(object):
    def __init__(self):
        self.split_feature = None   # 分裂的特征
        self.split_value = None     # 分裂的特征值
        self.leaf_value = None      # 叶子节点的值
        self.tree_left = None       # 左子树
        self.tree_right = None      # 右子树

    # 通过递归决策树找到样本所属叶子节点（用于预测）
    def cal_predict_value(self, dataset):
        if self.leaf_value is not None:
            return self.leaf_value
        elif dataset[self.split_feature] <= self.split_value:
            return self.tree_left.cal_predict_value(dataset)
        else:
            return self.tree_right.cal_predict_value(dataset)

# 随机森林
class RandomForestRegression(object):
    def __init__(self, tree_num, max_depth, min_samples_split, col_samples_rate, row_samples_rate, random_state):
        '''
        tree_num:          树数量
        max_depth:         树深度
        min_samples_split: 节点分裂所需的最小样本数量，小于该值节点终止分裂
        col_samples_rate:  列采样设置，默认sqrt。sqrt表示随机选择sqrt(n_features)个特征
        row_samples_rate:  行采样比例
        random_state:      随机种子，确保实验可重复
        '''
        self.tree_num = tree_num
        self.max_depth = max_depth 
        self.min_samples_split = min_samples_split
        self.col_samples_rate = col_samples_rate
        self.row_samples_rate = row_samples_rate
        self.random_state = random_state
        self.trees = None

    # 模型训练入口
    def fit(self, dataset, targets):
        if self.random_state:
            random.seed(self.random_state)
        random_state_stages = random.sample(range(self.tree_num), self.tree_num)
        
        # 列采样
        if self.col_samples_rate == "sqrt":
            self.col_samples_rate = int(math.sqrt(len(dataset.columns)))
        else:
            self.col_samples_rate = len(dataset.columns)
        
        # 并行建立多棵决策树
        self.trees = Parallel(n_jobs=-1, backend="threading")(
            delayed(self.parallel_build_trees)(dataset, targets, random_state)
                for random_state in random_state_stages)

    # 有放回抽样建立新的样本集
    def parallel_build_trees(self, dataset, targets, random_state):
        feature_samples = random.sample(list(dataset.columns), self.col_samples_rate)
        dataset_stage = dataset.loc[:, feature_samples]
        dataset_stage = dataset_stage.sample(n=int(self.row_samples_rate*len(dataset)), replace=True, 
                                        random_state=random_state).reset_index(drop=True)
        targets_stage = targets.sample(n=int(self.row_samples_rate*len(dataset)), replace=True, 
                                        random_state=random_state).reset_index(drop=True)
        tree = self.build_single_tree(dataset_stage, targets_stage, depth=0)
        return tree

    # 递归建立决策树
    def build_single_tree(self, dataset, targets, depth):
        # 样本小于分裂所需最小样本数量，则终止分裂
        if len(dataset) <= self.min_samples_split:
            tree = Tree()
            tree.leaf_value = self.cal_leaf_value(targets['rating'])
            return tree

        if depth < self.max_depth:
            best_split_feature, best_split_value = self.choose_best_feature(dataset, targets)
            left_dataset, right_dataset, left_targets, right_targets = \
                self.split_dataset(dataset, targets, best_split_feature, best_split_value)

            tree = Tree()
            tree.split_feature = best_split_feature
            tree.split_value = best_split_value
            tree.tree_left = self.build_single_tree(left_dataset, left_targets, depth+1)
            tree.tree_right = self.build_single_tree(right_dataset, right_targets, depth+1)
            return tree
        # 如果树的深度超过预设值，则终止分裂
        else:
            tree = Tree()
            tree.leaf_value = self.cal_leaf_value(targets['rating'])
            return tree

    # 选择最优分裂特征和分裂阈值
    def choose_best_feature(self, dataset, targets):
        best_split_gain = float("inf")
        best_split_feature = None
        best_split_value = None

        for feature in dataset.columns:
            if len(np.unique(dataset[feature])) <= 100:
                unique_values = np.unique(dataset[feature])
            # 如果该维度特征取值太多，则选择100个百分位值作为待选分裂阈值
            else: # unique去除数组中的重复数字并进行排序之后输出 percentile 求0%到100%的100个点
                unique_values = np.unique([np.percentile(dataset[feature], x)for x in np.linspace(0, 100, 100)])

            # 对可能的分裂阈值求分裂增益
            for split_value in unique_values:
                left_targets = targets[dataset[feature] <= split_value]
                right_targets = targets[dataset[feature] > split_value]
                split_gain = self.cal_r2(left_targets['rating'], right_targets['rating'])

                if split_gain < best_split_gain:
                    best_split_feature = feature
                    best_split_value = split_value
                    best_split_gain = split_gain
        return best_split_feature, best_split_value

    # 选择所有样本的均值作为叶子节点取值
    def cal_leaf_value(self, targets):
        return targets.mean()

    # 回归树采用平方误差作为指标来选择最优分裂点
    def cal_r2(self, left_targets, right_targets):
        gain = 0
        mean = left_targets.mean()
        for temp in left_targets:
            gain += (temp - mean) ** 2
        mean = right_targets.mean()
        for temp in right_targets:
            gain += (temp - mean) ** 2
        return gain

    # 根据最优特征的阈值将样本划分成左右两份，左边小于等于阈值，右边大于阈值
    def split_dataset(self, dataset, targets, split_feature, split_value):
        left_dataset = dataset[dataset[split_feature] <= split_value]
        left_targets = targets[dataset[split_feature] <= split_value]
        right_dataset = dataset[dataset[split_feature] > split_value]
        right_targets = targets[dataset[split_feature] > split_value]
        return left_dataset, right_dataset, left_targets, right_targets

    # 输入样本，得到预测值
    def predict(self, dataset):
        res = []
        for _, row in dataset.iterrows():
            pred_list = []
            # 统计每棵树的预测结果，再求平均作为最终预测值
            for tree in self.trees:
                pred_list.append(tree.cal_predict_value(row))
            res.append(sum(pred_list) / len(pred_list))
        return res

# 加载数据集
train_vectors = pd.DataFrame(np.load("code/regression/train_vectors.npy"))
train_rating = pd.DataFrame(np.load("code/regression/train_rating.npy").reshape(-1, 1), columns=['rating'])
valid_vectors = pd.DataFrame(np.load("code/regression/valid_vectors.npy"))
valid_rating = pd.DataFrame(np.load("code/regression/valid_rating.npy").reshape(-1, 1), columns=['rating'])
test_vectors = pd.DataFrame(np.load("code/regression/test_vectors.npy"))
test_id = np.load("code/regression/test_id.npy")
r1 = np.load("code/regression/train_rating.npy")
r2 = np.load("code/regression/valid_rating.npy")

# 随机森林训练
# x = []
# y1 = []
# y2 = []
# for i in range(1,11,1):
#     RF = RandomForestRegression(tree_num=5, max_depth=i, min_samples_split=200, col_samples_rate='sqrt',row_samples_rate=0.4,random_state=77)
#     start = time.time()
#     RF.fit(train_vectors, train_rating)
#     end = time.time()
#     a1 = math.sqrt(np.sum(np.square(RF.predict(train_vectors)-r1))/len(r1))
#     a2 = math.sqrt(np.sum(np.square(RF.predict(valid_vectors)-r2))/len(r2))
#     x.append(i)
#     y1.append(a1)
#     y2.append(a2)
#     print(i,"Running time: {:.4f}s".format(end-start))
#     print(a1)
#     print(a2)
# import matplotlib.pyplot as plt 
# plt.grid(True)
# plt.plot(x, y1, color='tab:blue', label='train set')
# plt.plot(x, y2, color='tab:orange', label='valid set')
# plt.title('RMSE of different max_depth')
# plt.xlabel('max_depth')
# plt.ylabel('RMSE')
# plt.legend()
# plt.show()

# 输出测试集预测结果
RF = RandomForestRegression(tree_num=5, max_depth=5, min_samples_split=420, col_samples_rate='sqrt',row_samples_rate=0.4,random_state=77)

start = time.time()
RF.fit(train_vectors, train_rating)
end = time.time()
print("Running time: {:.4f}s".format(end-start))
print(math.sqrt(np.sum(np.square(RF.predict(train_vectors)-r1))/len(r1)))
print(math.sqrt(np.sum(np.square(RF.predict(valid_vectors)-r2))/len(r2)))

test_predict = RF.predict(test_vectors)
test_output = pd.DataFrame({'id': test_id, 'humor_rating': test_predict})
test_output.to_csv('code/regression/output2.csv', index=None, encoding='utf8')  