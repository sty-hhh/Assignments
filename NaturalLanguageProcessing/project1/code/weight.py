#%%
import numpy as np
import pandas as pd
from nltk.tokenize.toktok import ToktokTokenizer
from gensim.models import Word2Vec
import matplotlib.pyplot as plt
import os

tokenizer=ToktokTokenizer()
data = pd.read_csv('clean_text.csv')

# 构建语料库
def tokenization(text):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]  
    return tokens

data['review']=data['review'].apply(tokenization)
# 建立训练集、验证集、测试集的语料库
train_corpus = data['review'][:30000]
valid_corpus = data['review'][30000:40000]
test_corpus  = data['review'][40000:50000]
train_labels = data['sentiment'][:30000]
valid_labels = data['sentiment'][30000:40000]
test_labels  = data['sentiment'][40000:50000]


w2v = Word2Vec.load('word2vec.model')
vocab = set(w2v.wv.index_to_key)
vocab_list = w2v.wv.index_to_key
vocab_list.insert(0,0)
vocab_size = len(vocab_list)
embed_size = 100
weight = np.zeros((vocab_size, embed_size),dtype='float32')
print(weight.shape)
print(vocab_size)

for i in range(1,vocab_size):
    weight[i,:] = w2v.wv[vocab_list[i]]
print(weight.shape)


train_vectors = []
for line in train_corpus:
    vector = []
    for word in line:
        if word in vocab:
            vector.append(vocab_list.index(word, 0, len(vocab_list)))
    train_vectors.append(vector) 
    
rev_len = [len(i) for i in train_vectors]
pd.Series(rev_len).hist()
plt.show()
pd.Series(rev_len).describe()

# valid_vectors = []
# for line in valid_corpus:
#     vector = []
#     for word in line:
#         if word in vocab:
#             vector.append(vocab_list.index(word, 0, len(vocab_list)))
#     valid_vectors.append(vector)  
# test_vectors = []
# for line in test_corpus:
#     vector = []
#     for word in line:
#         if word in vocab:
#             vector.append(vocab_list.index(word, 0, len(vocab_list)))
#     test_vectors.append(vector)
# # print(train_vectors)


# def padding(sentences, seq_len):
#     features = np.zeros((len(sentences), seq_len),dtype=int)
#     for i, review in enumerate(sentences):
#         if len(review) > seq_len:
#             features[i, :] = np.array(review)[:seq_len]
#         else:
#             features[i, -len(review):] = np.array(review)[:seq_len]
#     return features

# train_vectors = padding(train_vectors, 400)
# valid_vectors = padding(valid_vectors, 400)
# test_vectors = padding(test_vectors, 400)
# print(test_vectors.shape)


# # 保存numpy数组
# np.save('w2i/train_vectors.npy', train_vectors)
# np.save('w2i/valid_vectors.npy', valid_vectors)
# np.save('w2i/test_vectors.npy', test_vectors)
# np.save('w2i/train_labels.npy', train_labels)
# np.save('w2i/valid_labels.npy', valid_labels)
# np.save('w2i/test_labels.npy', test_labels)
# np.save('w2i/weight.npy', weight)
# # %%

# %%
