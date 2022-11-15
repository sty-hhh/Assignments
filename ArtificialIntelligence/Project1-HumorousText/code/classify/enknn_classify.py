#encoding = UTF-8
import pandas as pd
import numpy as np
import random
import math
from joblib import Parallel, delayed


class EnsembleKNN(object):
    def __init__(self):
        self.KSet = None  # 对应每个不同距离度量方式knn选择的k
        self.dis_type_Set = None  # 对应选择的距离度量方式 欧式距离 曼哈顿距离
        self.col_choice_Set = None  # 每个KNN选择的列
        self.row_choice_Set = None  # 每个KNN选择的行

    def ComputeDis(self, x, y, P):
        return np.sum(abs(np.array(x)-np.array(y))**P)**1/P
    '''
    测试
    对于集成KNN中的每个KNN子模型,在测试集上得到预测分类结果,然后利用投票法得到最终的分类
    '''
    def test(self, train_dataset, train_label, test_dataset):
        res = np.zeros(len(test_dataset))
        for i in range(len(self.KSet)):  # 第i个knn子模型
            k = self.KSet[i]
            dis_type = np.array(self.dis_type_Set[i])
            ColChoice = np.array(self.col_choice_Set[i])
            RowChoice = np.array(self.row_choice_Set[i])

            SampleTrainDataset = np.array(train_dataset)[RowChoice, :]  
            SampleTrainDataset = np.array(SampleTrainDataset)[:, ColChoice]
            SampleTrainLabel = np.array(train_label)[RowChoice]
            SampleTestDataset = np.array(test_dataset)[:, ColChoice]
            temp = []
            for line in SampleTestDataset:
                dis_list = []
                for ID, record in enumerate(SampleTrainDataset):
                    dis = self.ComputeDis(line, record, dis_type)
                    l = []
                    l.append(dis)
                    l.append(SampleTrainLabel[ID])  # 训练集中编号为ID的数据对应的标签
                    dis_list.append(l)
                dis_list = sorted(dis_list, key=(lambda x: x[0]))  # 按距离升序排序
                dict1 = {}
                j = 0
                while j < k:
                    if dis_list[j][1] not in dict1:
                        dict1[dis_list[j][1]] = 1  # 统计前k篇文档中每个类别各有多少文章
                    else:
                        dict1[dis_list[j][1]] += 1
                    j += 1
                temp.append(max(dict1, key=lambda x: dict1[x]))  # 类别取众数
            res = res + np.array(temp)
        ans = []
        for i in range(len(res)):
            if res[i] >= len(self.KSet)/2:
                ans.append(1)
            else:
                ans.append(0)
        return np.array(ans)
    '''
    训练
    通过定义一个EnsembleKNN实例，然后调用train()，得到EnsembleKNN模型。train_dataset,train_label:训练数据集
    valid_dataset,valid_label:验证集
    dis_type:字符串列表,每一个字符串代表一个距离类型,len(dis_type)表示总的子KNN模型。
    '''
    def train(self, train_dataset, train_label, valid_dataset, valid_label, dis_type, random_state=None):
        if random_state:
            random.seed(random_state)
        random_seed_list = []
        for i in range(2*len(dis_type)):
            random_seed_list.append(i+random_state)#设置随机种子
        ColSampleNum = 0.8*len(train_dataset[0])#决定为每个子KNN模型选择的特征的数目
        RowSampleNum = 0.8*len(train_dataset)#决定为每个子KNN模型选择的数据数目
        self.KSet, self.dis_type_Set, self.col_choice_Set, self.row_choice_Set = zip(*Parallel(n_jobs=-1, verbose=0, backend="threading")(
            delayed(self.EnsembleModel)(train_dataset, train_label, valid_dataset, valid_label,
                                              dis_type[i], ColSampleNum, RowSampleNum, random_seed_list[2*i], random_seed_list[2*i+1])#并行
            for i in range(len(dis_type))))
    '''
    train_dataset:全部的训练集数据
    train_label:全部的训练集标签
    valid_dataset:全部的验证集数据
    valid_label:全部的验证集标签
    dis_type:指定的距离度量方式列表,将根据不同的距离度量方式,训练出len(dis_type)个knn子模型进行集成
    ColSampleNum:采样的特征得数目
    RowSampleNum:采样得数据的数目
    random_state_row/random_state_col:随机种子,由于数据和特征均要用到random.sample进行随机采样,为了保证实验的可重复性,每一列,每一行的
    选择均设置随机种子
    '''
    def EnsembleModel(self, train_dataset, train_label, valid_dataset, valid_label, dis_type, ColSampleNum, RowSampleNum, random_state_row, random_state_col):
        random.seed(random_state_col)
        SampleColIndex = random.sample(
            range(len(train_dataset[0])), int(ColSampleNum))#随机采样特征
        random.seed(random_state_row)
        SampleRowIndex = random.sample(
            range(len(train_dataset)), int(RowSampleNum))#随机采样数据
        SampleTrainDataset = np.array(train_dataset)[SampleRowIndex, :]#得到采样后的训练集
        SampleTrainDataset = SampleTrainDataset[:, SampleColIndex]
        SampleTrainLabel = np.array(train_label)[SampleRowIndex]#得到采样后的训练集标签
        SampleValidDataset = np.array(valid_dataset)[:, SampleColIndex]#只对验证集进行特征采样
        k = self.KNNSubModel(SampleTrainDataset.tolist(), SampleTrainLabel.tolist(
        ), SampleValidDataset.tolist(), valid_label, dis_type)
        return k, dis_type, SampleColIndex, SampleRowIndex#该KNN子模型由该4个数据进行描述
    '''
    KNNSubModel:
    SampleTrainDataset:经过采样后的训练集
    SampleTrainLabel:经过采样后的训练集标签集合
    SampleValidDataset:经过采样后的验证集
    SampleValidLabel:经过采样后的验证集标签集合
    dis_type:该KNN子模型选择的距离度量方式
    返回值:该KNN子模型对应的最优的k
    '''
    def KNNSubModel(self, SampleTrainDataset, SampleTrainLabel, SampleValidDataset, SampleValidLabel, dis_type):
        k_to_accuracy = {}
        for k in range(3,80):
            predict_res = []
            for line in SampleValidDataset:
                dis_list = []
                for ID, record in enumerate(SampleTrainDataset):
                    dis = self.ComputeDis(line, record, dis_type)
                    l = []
                    l.append(dis)
                    l.append(SampleTrainLabel[ID])  # 训练集中编号为ID的文档对应的标签
                    dis_list.append(l)
                dis_list = sorted(dis_list, key=(lambda x: x[0]))  # 按距离升序排序
                dict1 = {}
                j = 0
                while j < k:
                    if dis_list[j][1] not in dict1:
                        dict1[dis_list[j][1]] = 1  # 统计前k篇文档中每个类别各有多少文章
                    else:
                        dict1[dis_list[j][1]] += 1
                    j += 1
                predict_res.append(max(dict1, key=lambda x: dict1[x]))  # 类别取众数
            accuracy = np.sum(np.array(predict_res) == np.array(
                SampleValidLabel))/len(predict_res)
            k_to_accuracy[k] = accuracy

        return max(k_to_accuracy, key=k_to_accuracy.get)#选择最高的准确率对应的K


if __name__ == '__main__':
    train_vectors = np.load("code/classify/train_vectors.npy")
    valid_vectors = np.load("code/classify/valid_vectors.npy")
    test_vectors = np.load("code/classify/test_vectors.npy")
    train_labels = np.load("code/classify/train_labels.npy")
    valid_labels = np.load("code/classify/valid_labels.npy")
    print(train_vectors.shape)
    print(train_labels.shape)
    print(valid_vectors.shape)
    print(valid_labels.shape)
    print(test_vectors.shape)
    hhh = EnsembleKNN()
    hhh.train(train_vectors.tolist(), train_labels.tolist(), valid_vectors.tolist(), valid_labels.tolist(), [1,2,3], 100)
    valid_res = hhh.test(train_vectors.tolist(),train_labels.tolist(), valid_vectors.tolist())
    print("验证集准确率:%f"%(np.sum(np.array(valid_res)==np.array(valid_labels))/len(valid_labels)))
    res = hhh.test(train_vectors.tolist(),train_labels.tolist(), test_vectors.tolist())
    temp = res.reshape(-1, 1).tolist()
    res = [line[0] for line in temp]
    test_output = pd.DataFrame({'id': np.arange(len(res))+8001, 'is_humor': res})
    test_output.to_csv('code/classify/enknn.csv', index=None, encoding='utf8')  