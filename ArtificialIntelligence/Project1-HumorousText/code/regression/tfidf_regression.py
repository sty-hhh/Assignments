#encoding=UTF-8
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
import jieba
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk
import read_regression as rd


nltk.download('stopwords')
stop = stopwords.words('english')
porter = PorterStemmer()

def judge_pure_english(keyword):
    return all(((ord(c)>64 and ord(c)<91) or (ord(c)>96 and ord(c)<128)) for c in keyword)

def build(data):
    sentences = []
    for content in data:
        tokens = list(jieba.cut(content, cut_all=False))
        words = []
        for word in tokens:
            if judge_pure_english(word):
                temp = porter.stem(word)
                if temp not in stop:
                    words.append(temp)
        sentence = " " .join(words)
        sentences.append(sentence)  
    return sentences

train_corpus = build(rd.train_data)
valid_corpus = build(rd.valid_data)
test_corpus = build(rd.test_data)


vectorizer = CountVectorizer(stop_words='english')
# 先fit训练传入的文本数据，然后对文本数据进行标记并转换为稀疏计数矩阵
train_counts = vectorizer.fit_transform(train_corpus)
valid_counts = vectorizer.transform(valid_corpus)
test_counts = vectorizer.transform(test_corpus)


transform = TfidfTransformer()    # 使用TF-IDF（词频、逆文档频率）应用于稀疏矩阵
train_vectors = np.array(transform.fit_transform(train_counts).toarray())
valid_vectors = np.array(transform.transform(valid_counts).toarray())
test_vectors = np.array(transform.transform(test_counts).toarray())
print(train_vectors.shape)
print(valid_vectors.shape)
print(test_vectors.shape)

np.save("train_vectors.npy", train_vectors)
np.save("valid_vectors.npy", valid_vectors)
np.save("test_vectors.npy", test_vectors)
np.save("train_labels.npy", np.array(rd.train_rating))
np.save("valid_labels.npy", np.array(rd.valid_rating))
np.save("test_id.npy", np.array(rd.test_id))



