#encoding=UTF-8
import pandas as pd
import numpy as np
import random
import math
from joblib import Parallel, delayed

    
class EnsembleKNN(object):
    def __init__(self):
        self.KSet = None     #对应每个不同距离度量方式knn选择的k
        self.dis_type_Set = None #对应选择的距离度量方式 欧式距离 曼哈顿距离
        self.col_choice_Set = None #每个KNN选择的列
        self.row_choice_Set = None #每个KNN选择的行
    def ComputeDis(self,x,y,P):
        return np.sum(abs(np.array(x)-np.array(y))**P)**1/P
    '''
    测试
    对于集成KNN中的每个KNN子模型,在测试集上得到预测分类结果,然后利用投票法得到最终的分类
    '''
    def test(self,train_dataset,train_rating,test_dataset):
        res = np.zeros((1,len(test_dataset)))
        for i in range(len(self.KSet)):#第i个knn子模型
            k = self.KSet[i]
            dis_type = np.array(self.dis_type_Set[i])
            ColChoice = np.array(self.col_choice_Set[i])
            RowChoice = np.array(self.row_choice_Set[i])

            SampleTrainDataset = np.array(train_dataset)[RowChoice,:]#选择
            SampleTrainDataset = np.array(SampleTrainDataset)[:,ColChoice]
            SampleTrainRating = np.array(train_rating)[RowChoice]
            SampleTestDataset = np.array(test_dataset)[:,ColChoice]
            temp = []
            for line in SampleTestDataset:
                dis_list = []
                for ID,record in enumerate(SampleTrainDataset):
                    dis = self.ComputeDis(line,record,dis_type)
                    l = []
                    l.append(dis)
                    l.append(SampleTrainRating[ID])#训练集中编号为ID的文档对应的分数
                    dis_list.append(l)
                dis_list = sorted(dis_list,key=(lambda x:x[0]))#按距离升序排序
                normalized = 0#归一化,距离越近,占的比重越大
                test_rating = 0
                for i in range(k):
                    normalized += 1/dis_list[i][0]
                    test_rating += dis_list[i][1]/dis_list[i][0]
                temp.append(test_rating/normalized)
            res = res + np.array(temp)
        res = res / len(self.KSet)#集成所有knn子模型的结果取平均
        return res

    '''
    dis_type = 距离类型列表
    random_state:设置随机种子,使得实验可重复
    训练
    通过定义一个EnsembleKNN实例，然后调用train()，得到EnsembleKNN模型。train_dataset,train_label:训练数据集
    valid_dataset,valid_label:验证集
    dis_type:字符串列表,每一个字符串代表一个距离类型,len(dis_type)表示总的子KNN模型。
    '''
    def train(self,train_dataset,train_rating,target_dataset,target_rating,dis_type,random_state=None):
        if random_state:
            random.seed(random_state)
        random_seed_list = []
        for i in range(2*len(dis_type)):
            random_seed_list.append(i+random_state)
        ColSampleNum = 0.8*len(train_dataset[0])    #取特征总数的0.8
        RowSampleNum = 0.8*len(train_dataset)       #取数据总数的0.8
        self.KSet,self.dis_type_Set,self.col_choice_Set,self.row_choice_Set =  zip(*Parallel(n_jobs=-1, verbose=0, backend="threading")(
            delayed(self.EnsembleModel)(train_dataset, train_rating, target_dataset,target_rating,dis_type[i],ColSampleNum,RowSampleNum,random_seed_list[2*i],random_seed_list[2*i+1])
                for i in range(len(dis_type))))#并行计算
        
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
    def EnsembleModel(self,train_dataset,train_rating,target_dataset,target_rating,dis_type,ColSampleNum,RowSampleNum,random_state_row,random_state_col):
        random.seed(random_state_col)
        SampleColIndex = random.sample(range(len(train_dataset[0])),int(ColSampleNum))#随机选择特征
        random.seed(random_state_row)
        SampleRowIndex = random.sample(range(len(train_dataset)),int(RowSampleNum))#随机选择行
        SampleTrainDataset = np.array(train_dataset)[SampleRowIndex,:]
        SampleTrainDataset = SampleTrainDataset[:,SampleColIndex]
        SampleTrainRating = np.array(train_rating)[SampleRowIndex]
        SampleTargetDataset = np.array(target_dataset)[:,SampleColIndex]
        k = self.KNNSubModel(SampleTrainDataset.tolist(),SampleTrainRating.tolist(),SampleTargetDataset.tolist(),target_rating,dis_type)
        return k,dis_type,SampleColIndex,SampleRowIndex
    '''
    KNNSubModel:
    SampleTrainDataset:经过采样后的训练集
    SampleTrainLabel:经过采样后的训练集标签集合
    SampleValidDataset:经过采样后的验证集
    SampleValidLabel:经过采样后的验证集标签集合
    dis_type:该KNN子模型选择的距离度量方式
    返回值:该KNN子模型对应的最优的k
    '''
    def KNNSubModel(self,SampleTrainDataset,SampleTrainRating,SampleTargetDataset,SampleTragetRating,dis_type):
        k_to_error = {}#
        for k in range(3,80):
            test_res = []
            for line in SampleTargetDataset:
                dis_list = []
                for ID,record in enumerate(SampleTrainDataset):
                    dis = self.ComputeDis(line,record,dis_type)
                    l = []
                    l.append(dis)
                    l.append(SampleTrainRating[ID])#训练集中编号为ID的文档对应的标签
                    dis_list.append(l)
                dis_list = sorted(dis_list,key=(lambda x:x[0]))#按距离升序排序
                normalized = 0
                test_rating = 0
                for i in range(k):
                    normalized += 1/dis_list[i][0]
                    test_rating += dis_list[i][1]/dis_list[i][0]
                test_res.append(test_rating/normalized)
            error = np.power(np.sum(np.square(np.array(test_res)-np.array(SampleTragetRating)))/len(test_res),0.5)
            k_to_error[k] = error
            
        return min(k_to_error,key=k_to_error.get)


if __name__ == '__main__':
    train_vectors = np.load("code/regression/train_vectors.npy")
    valid_vectors = np.load("code/regression/valid_vectors.npy")
    valid_rating = np.load("code/regression/valid_rating.npy")
    train_rating = np.load("code/regression/train_rating.npy")
    test_id = np.load("code/regression/test_id.npy")
    test_vectors = np.load("code/regression/test_vectors.npy")
    hhh = EnsembleKNN()
    hhh.train(train_vectors.tolist(),train_rating.tolist(),valid_vectors.tolist(),valid_rating.tolist(),[1,2],100)
    valid_res = hhh.test(train_vectors.tolist(),train_rating.tolist(),valid_vectors.tolist())
    print('验证集误差%f'%(np.power(np.sum(np.square(np.array(valid_res)-np.array(valid_rating)))/len(valid_rating),0.5)))
    res = hhh.test(train_vectors.tolist(),train_rating.tolist(),test_vectors.tolist())
    temp = res.reshape(-1,1).tolist()
    res = [line[0] for line in temp]
    dict = {'id':test_id,'humor_rating':res}   
    df = pd.DataFrame(dict)
    df.to_csv('code/regression/output.csv',index=None, encoding='utf8')
