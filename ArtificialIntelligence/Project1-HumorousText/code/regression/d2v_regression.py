#encoding=UTF-8
import numpy as np
import pandas as pd
import gensim
import read_regression as rd
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk

# 下载停用词和stemmer
nltk.download('stopwords')
stop = set(stopwords.words('english'))
porter = PorterStemmer()

# 去除脏数据
def judge_pure_english(keyword):
    return all(((ord(c)>64 and ord(c)<91) or (ord(c)>96 and ord(c)<128)) for c in keyword)

# 建立语料库
def build_corpus(data_set, rating_set=None, tokens_only=True):
    print(len(data_set))
    for i, line in enumerate(data_set):
        tokens = gensim.utils.simple_preprocess(line)   # 分词
        sentence = []
        for word in tokens:
            if word not in stop and judge_pure_english(word):   # 去除停用词和脏数据
                temp = porter.stem(word)    # 词干化
                sentence.append(temp)
        if tokens_only:
            yield sentence
        else:
            yield gensim.models.doc2vec.TaggedDocument(sentence, [rating_set[i]])

# 建立训练集、验证集、测试集的语料库
train_corpus = list(build_corpus(rd.train_data, rd.train_rating,False))
valid_corpus = list(build_corpus(rd.valid_data))
test_corpus = list(build_corpus(rd.test_data))

# doc2vec训练
model = gensim.models.doc2vec.Doc2Vec(vector_size=100, min_count=2, epochs = 20,workers = 4, window = 2)
model.build_vocab(train_corpus)
model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)


# 将数据集中的每个句子映射为向量
train_vectors = []
for i in range(len(train_corpus)):
    inferred_vector = model.infer_vector(train_corpus[i].words)
    train_vectors.append(inferred_vector)
valid_vectors = []
for i in range(len(valid_corpus)):
    inferred_vector = model.infer_vector(valid_corpus[i])
    valid_vectors.append(inferred_vector)
test_vectors = []
for i in range(len(test_corpus)):
    inferred_vector = model.infer_vector(test_corpus[i])
    test_vectors.append(inferred_vector)

# 保存为numpy数组
np.save("code/regression/train_vectors.npy", np.array(train_vectors))
np.save("code/regression/valid_vectors.npy", np.array(valid_vectors))
np.save("code/regression/test_vectors.npy", np.array(test_vectors))
np.save("code/regression/train_rating.npy", np.array(rd.train_rating))
np.save("code/regression/valid_rating.npy", np.array(rd.valid_rating))
np.save("code/regression/test_id.npy", np.array(rd.test_id))
