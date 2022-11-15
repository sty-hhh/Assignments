from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
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
train_corpus = data['review'][:30000]
valid_corpus = data['review'][30000:40000]
test_corpus  = data['review'][40000:50000]
train_labels = data['sentiment'][:30000]
valid_labels = data['sentiment'][30000:40000]
test_labels  = data['sentiment'][40000:50000]

vectorizer = CountVectorizer(stop_words='english',min_df=5,dtype='float32')
# 先fit训练传入的文本数据，然后对文本数据进行标记并转换为稀疏计数矩阵
train_counts = vectorizer.fit_transform(train_corpus)
valid_counts = vectorizer.transform(valid_corpus)
test_counts = vectorizer.transform(test_corpus)

transform = TfidfTransformer()    # 使用TF-IDF（词频、逆文档频率）应用于稀疏矩阵
train_vectors = np.array(transform.fit_transform(train_counts).toarray())
valid_vectors = np.array(transform.transform(valid_counts).toarray())
test_vectors = np.array(transform.transform(test_counts).toarray())

# 保存numpy数组
np.save('tfidf/train_vectors.npy', train_vectors)
np.save('tfidf/valid_vectors.npy', valid_vectors)
np.save('tfidf/test_vectors.npy', test_vectors)
np.save('tfidf/train_labels.npy', train_labels)
np.save('tfidf/valid_labels.npy', valid_labels)
np.save('tfidf/test_labels.npy', test_labels)