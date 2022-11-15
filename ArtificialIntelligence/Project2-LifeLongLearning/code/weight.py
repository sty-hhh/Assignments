#%%
import numpy as np
import pandas as pd
from nltk.tokenize.toktok import ToktokTokenizer
from gensim.models import Word2Vec
import matplotlib.pyplot as plt
import os

embedding_index = {}
f = open('glove/glove.6b.300d.txt', encoding="utf8")
for line in f: # or f.readlines() instead of f.readline()
    val = line.split()
    word = val[0]
    coef = np.asarray(val[1:], dtype ='float32')
    embedding_index[word] = coef
f.close()

print(embedding_index['the'])
#%%
train1 = pd.read_csv('data/comp/train.csv')
valid1 = pd.read_csv('data/comp/valid.csv')
test1 = pd.read_csv('data/comp/test.csv')
train2 = pd.read_csv('data/rec/train.csv')
valid2 = pd.read_csv('data/rec/valid.csv')
test2 = pd.read_csv('data/rec/test.csv')
train3 = pd.read_csv('data/sci/train.csv')
valid3 = pd.read_csv('data/sci/valid.csv')
test3 = pd.read_csv('data/sci/test.csv')
train4 = pd.read_csv('data/talk/train.csv')
valid4 = pd.read_csv('data/talk/valid.csv')
test4 = pd.read_csv('data/talk/test.csv')
print(len(train4['text']))
print(valid4['text'][0])

#%%
train1 = pd.concat([train1,valid1],axis=0,ignore_index=True)
train2 = pd.concat([train2,valid2],axis=0,ignore_index=True)
train3 = pd.concat([train4,valid3],axis=0,ignore_index=True)
train4 = pd.concat([train4,valid4],axis=0,ignore_index=True)

tokenizer=ToktokTokenizer()
def tokenization(text):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]  
    return tokens
train1['text']=train1['text'].apply(tokenization)
train2['text']=train2['text'].apply(tokenization)
train3['text']=train3['text'].apply(tokenization)
train4['text']=train4['text'].apply(tokenization)
test1['text']=test1['text'].apply(tokenization)
test2['text']=test2['text'].apply(tokenization)
test3['text']=test3['text'].apply(tokenization)
test4['text']=test4['text'].apply(tokenization)

print(train4['text'][0])
#%%
w = set()
w2i = {}
print(len(train4['text']))
#%%
for line in train1['text']:
    for word in line:
        w.add(word)
for line in train2['text']:
    for word in line:
        w.add(word)
for line in train3['text']:
    for word in line:
        w.add(word)
for line in train4['text']:
    for word in line:
        w.add(word)

print(len(w))
#%%
for i,word in enumerate(w): 
    w2i[word] = i+1


#%%
train_data1 = []
train_data2 = []
train_data3 = []
train_data4 = []
test_data1 = []
test_data2 = []
test_data3 = []
test_data4 = []

for line in train1['text']:
    temp = []
    for word in line:
        temp.append(w2i[word])
    train_data1.append(temp)
for line in train2['text']:
    temp = []
    for word in line:
        temp.append(w2i[word])
    train_data2.append(temp)
for line in train3['text']:
    temp = []
    for word in line:
       temp.append(w2i[word])
    train_data3.append(temp)
for line in train4['text']:
    temp = []
    for word in line:
        temp.append(w2i[word])
    train_data4.append(temp)
    
print(len(train1['text']))
print(len(train2['text']))
print(len(train3['text']))
print(len(train4['text']))

print(len(train1['text'][0]))
print(len(train2['text'][0]))
print(len(train3['text'][0]))
print(len(train4['text'][0]))

print(len(train_data1[0]))
print(len(train_data2[0]))
print(len(train_data3[0]))
print(len(train_data4[0]))

#%%
test_data1 = []
test_data2 = []
test_data3 = []
test_data4 = []
for line in test1['text']:
    temp = []
    for word in line:
        if word in w:
            temp.append(w2i[word])
    test_data1.append(temp)
for line in test2['text']:
    temp = []
    for word in line:
        if word in w:
            temp.append(w2i[word])
    test_data2.append(temp)
for line in test3['text']:
    temp = []
    for word in line:
        if word in w:
            temp.append(w2i[word])
    test_data3.append(temp)
for line in test4['text']:
    temp = []
    for word in line:
        if word in w:
            temp.append(w2i[word])
    test_data4.append(temp)
    
print(test_data1[10])
print(len(test_data1[0]))
print(len(test_data2[0]))
print(len(test_data3[0]))
print(len(test_data4[0]))


#%%
rev_len = [len(i) for i in train_data4]
pd.Series(rev_len).hist()
plt.show()
pd.Series(rev_len).describe()

#%%

def padding(sentences, seq_len):
    features = np.zeros((len(sentences), seq_len),dtype=int)
    for i, review in enumerate(sentences):
        if len(review) > seq_len:
            features[i, :] = np.array(review)[:seq_len]
        else:
            features[i, -len(review):] = np.array(review)[:seq_len]
    return features

train_data1 = padding(train_data1, 80)
train_data2 = padding(train_data2, 80)
train_data3 = padding(train_data3, 80)
train_data4 = padding(train_data4, 80)
test_data1 = padding(test_data1, 80)
test_data2 = padding(test_data2, 80)
test_data3 = padding(test_data3, 80)
test_data4 = padding(test_data4, 80)
print(train_data1.shape)


#%%

Embedding_dim = 300
weight = np.zeros((len(w2i)+1, Embedding_dim),dtype='float32')

for word, num in w2i.items():
    embedding_vector = embedding_index.get(word) 
    if embedding_vector is not None:
        weight[num] = embedding_vector
for word, num in w2i.items():
    embedding_vector = embedding_index.get(word) 
    if embedding_vector is not None:
        weight[num] = embedding_vector
for word, num in w2i.items():
    embedding_vector = embedding_index.get(word) 
    if embedding_vector is not None:
        weight[num] = embedding_vector
for word, num in w2i.items():
    embedding_vector = embedding_index.get(word) 
    if embedding_vector is not None:
        weight[num] = embedding_vector
        
print(weight[10:20])
#%%
print(test_data1.shape)
train_label1 = np.array(train1['labels'])
train_label2 = np.array(train2['labels'])
train_label3 = np.array(train3['labels'])
train_label4 = np.array(train4['labels'])
test_label1 = np.array(test1['labels'])
test_label2 = np.array(test2['labels'])
test_label3 = np.array(test3['labels'])
test_label4 = np.array(test4['labels'])
print(train_label1[:5])
np.save('w2i/train_label1.npy', train_label1)
np.save('w2i/train_label2.npy', train_label2)
np.save('w2i/train_label3.npy', train_label3)
np.save('w2i/train_label4.npy', train_label4)

np.save('w2i/test_label1.npy', test_label1)
np.save('w2i/test_label2.npy', test_label2)
np.save('w2i/test_label3.npy', test_label3)
np.save('w2i/test_label4.npy', test_label4)

print(type(weight[0][0]))
#%%
# 保存numpy数组
np.save('w2i/train_data1.npy', train_data1)
np.save('w2i/train_data2.npy', train_data2)
np.save('w2i/train_data3.npy', train_data3)
np.save('w2i/train_data4.npy', train_data4)
np.save('w2i/test_data1.npy', test_data1)
np.save('w2i/test_data2.npy', test_data2)
np.save('w2i/test_data3.npy', test_data3)
np.save('w2i/test_data4.npy', test_data4)
np.save('w2i/weight.npy', weight)

print(train4['text'][0])
print(train_data4[0])
print(embedding_index.get('gun'))
# print(weight[44908])
# %%
