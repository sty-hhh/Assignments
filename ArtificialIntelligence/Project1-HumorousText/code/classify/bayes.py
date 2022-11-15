# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
from timeit import default_timer as timer
#验证集 0.8454 test:0.8
#
#lamda 0.1 验证集 0.8246
#lamda 0.2 验证集 0.8338
#lamda 0.3 验证集 0.8321
#lamda 0.4 验证集 0.8308
#lamda 0.5 验证集 0.8242
#lamda 0.6 验证集 0.8208
#lamda 0.7 验证集 0.8175
#lamda 0.8 验证集 0.8117

#text = w1,w2,w3...wn
#P(w1,w2,w3,...wn|humor) = P(w1|humor)*P(w2|humor)*P(w3|humor)...P(wn|humor)
#P(humor|text) 正比于 P(humor)*P(w1|humor)*P(w2|humor)*P(w3|humor)...P(wn|humor)
#单词w在类别class中出现的条件概率等于w在所有属于class的文档中出现的次数/所有属于class的文档中的单词总数

def train(trainVectors,trainLabels):
    TextNum = len(trainVectors)				            #总的文档数目
    lenDocVec = len(trainVectors[0])				    #文本向量长度
    PriorHumor = sum(trainLabels)/float(TextNum)	    #文档属于幽默类的概率
    WordNumHumor = np.ones(lenDocVec)                   #每个单词在幽默类文档中出现的次数,初始化为1,因为某些
                                                        #单词可能不出现在训练集的任何文档中,导致计算出的条件
                                                        #概率为0
    WordNumNotHumor = np.ones(lenDocVec)	            #每个单词在不幽默文档中出现的次数，初始化为1,拉普拉斯平滑                                         
    NotHumorWordSum = 1                                 #幽默文档的单词总数
    HumorWordSum = 1                    	            #不幽默文档的单词总数
    for i in range(TextNum):
        if trainLabels[i] == 1:							
            WordNumHumor += trainVectors[i]
            HumorWordSum += sum(trainVectors[i])
        else:										    
            WordNumNotHumor += trainVectors[i]
            NotHumorWordSum += sum(trainVectors[i])
    HumorCondP = np.log(WordNumHumor/HumorWordSum)		#WordNumHumor/HumorWordSum=每一个单词在幽默文档中出现的频率,取对数，防止下溢出          
    NotHumorCondP = np.log(WordNumNotHumor/NotHumorWordSum) #WordNumHumor/NotHumorWordSum=每一个单词在不幽默文档中出现的频率
    return HumorCondP,NotHumorCondP,PriorHumor				#返回属于幽默类的条件概率数组，属于非幽默类的条件概率数组，文档属于幽默类的先验概率

def test(testVector, NotHumorCondP, HumorCondP, PriorHumor):
    Humor = sum(testVector*HumorCondP) + np.log(PriorHumor)  #没有直接和0.5相比,因为没有归一化 
                                                             #乘以一个测试向量作为权重,因为对于文本向量表示来说 /
                                                             #一个词的取值越大,表明这个词对于判断这个文本的特征越重要.
    NotHumor = sum(testVector*NotHumorCondP) + np.log(1.0 - PriorHumor)
    if Humor > NotHumor:
        return 1
    else: 
        return 0

train_vectors = np.load("code/classify/train_vectors_TFIDF.npy")
valid_vectors = np.load("code/classify/valid_vectors_TFIDF.npy")
test_vectors = np.load("code/classify/test_vectors_TFIDF.npy")
train_labels = np.load("code/classify/train_labels_TFIDF.npy")
valid_labels = np.load("code/classify/valid_labels_TFIDF.npy")

HumorCondP,NotHumorCondP,PriorHumor	= train(train_vectors, train_labels)  #训练朴素贝叶斯模型
count = 0                                                          
for i,line in enumerate(valid_vectors):                                                
    if test(line, NotHumorCondP, HumorCondP, PriorHumor) == valid_labels[i]:    
        count += 1                                                 

print('accuracy: %f' % (float(count) / len(valid_vectors)))


test_predict = []
for i,line in enumerate(test_vectors):                                                #遍历测试集
    test_predict.append(test(line,NotHumorCondP, HumorCondP, PriorHumor))
t2 = timer()

test_output = pd.DataFrame({'id': np.arange(len(test_predict))+8001, 'is_humor': test_predict})
test_output.to_csv('code/classify/bayes.csv', index=None, encoding='utf8')  
