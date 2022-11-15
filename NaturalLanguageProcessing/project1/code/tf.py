from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import numpy as np
import pandas as pd
import time
import os
from nltk.tokenize.toktok import ToktokTokenizer

tokenizer=ToktokTokenizer()
start = time.time()


data = pd.read_csv('clean_text.csv')


# 建立训练集、验证集、测试集的语料库
train_corpus = list(data['review'][:30000])
valid_corpus = list(data['review'][30000:40000])
test_corpus  = list(data['review'][40000:50000])
train_labels = data['sentiment'][:30000]
valid_labels = data['sentiment'][30000:40000]
test_labels  = data['sentiment'][40000:50000]

vectorizer = CountVectorizer(stop_words='english',min_df=5,dtype='float32')
# 先fit训练传入的文本数据，然后对文本数据进行标记并转换为稀疏计数矩阵
train_vectors = np.array(vectorizer.fit_transform(train_corpus).toarray())
valid_vectors = np.array(vectorizer.transform(valid_corpus).toarray())
test_vectors = np.array(vectorizer.transform(test_corpus).toarray())

print(train_vectors.dtype)
start = time.time()

for i in range(train_vectors.shape[0]):
    train_vectors[i] = train_vectors[i] / len(train_corpus[i].split())
for i in range(valid_vectors.shape[0]):
    valid_vectors[i] = valid_vectors[i] / len(valid_corpus[i].split())
for i in range(test_vectors.shape[0]):
    test_vectors[i] = test_vectors[i] / len(test_corpus[i].split())
    
print(train_vectors.dtype)
print(train_vectors.shape)

# 保存numpy数组
np.save('tf/train_vectors.npy', train_vectors)
np.save('tf/valid_vectors.npy', valid_vectors)
np.save('tf/test_vectors.npy', test_vectors)
np.save('tf/train_labels.npy', train_labels)
np.save('tf/valid_labels.npy', valid_labels)
np.save('tf/test_labels.npy', test_labels)

end = time.time()
print('Running time: {:.4f}s'.format(end-start))

