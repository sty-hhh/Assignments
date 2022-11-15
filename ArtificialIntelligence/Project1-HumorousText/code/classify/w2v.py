#encoding=UTF-8
import numpy as np
import jieba
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
import read_classification as rd
from gensim.models import Word2Vec

# 下载停用词和stemmer
nltk.download('stopwords')
stop = stopwords.words('english')
porter = PorterStemmer()

# 去除脏数据
def judge_pure_english(keyword):
    return all(((ord(c)>64 and ord(c)<91) or (ord(c)>96 and ord(c)<128)) for c in keyword)

# 构建语料库
def build(data):
    sentences = []
    for content in data:
        tokens = list(jieba.cut(content, cut_all=False))
        sentence = []
        for word in tokens:
            if judge_pure_english(word):
                temp = porter.stem(word)
                if temp not in stop:
                    sentence.append(temp)
        sentences.append(sentence)
    return sentences

# 将词语vector转为句子vector
def make_sentence(corpus, bow):
    vectors = []
    for line in corpus:
        cnt = 0
        s = np.zeros(100)
        for word in line:
            if word in bow:
                cnt += 1
                vec = np.array(model.wv[word])
                s = s + np.array(vec)
        if cnt!=0:
            s = s / cnt
        s = list(s)
        vectors.append(s)
    return  np.array(vectors)

# 建立训练集、验证集、测试集的语料库
train_corpus = build(rd.train_data)
valid_corpus = build(rd.valid_data)
test_corpus = build(rd.test_data)

# word2vec训练
model = Word2Vec(sentences=train_corpus,vector_size=100, min_count=2, workers = 4, window = 2)
model.save("word2vec.model")
model.train(train_corpus, total_examples=model.corpus_count, epochs=40)

train_vectors = make_sentence(train_corpus, model.wv.index_to_key)
valid_vectors = make_sentence(valid_corpus, model.wv.index_to_key)
test_vectors = make_sentence(test_corpus, model.wv.index_to_key)

# 保存numpy数组
np.save("code/classify/train_vectors.npy", train_vectors)
np.save("code/classify/valid_vectors.npy", valid_vectors)
np.save("code/classify/test_vectors.npy", test_vectors)
np.save("code/classify/train_labels.npy", np.array(rd.train_labels))
np.save("code/classify/valid_labels.npy", np.array(rd.valid_labels))