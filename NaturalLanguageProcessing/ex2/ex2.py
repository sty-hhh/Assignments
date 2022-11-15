import requests
import lxml
from bs4 import BeautifulSoup
from xlwt import *
import jieba
from gensim.test.utils import common_texts
from gensim.models import Word2Vec
import re

# 爬虫
url = "https://news.ifeng.com/c/89TNORdIths"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}
f = requests.get(url, headers = headers)
soup = BeautifulSoup(f.content, 'lxml')
title = soup.find('div', {'class': 'caption-3nDTQcf1'}).find('h1', {'class': 'topic-2Eq5D0Zm'})
contents = soup.find('div', {'class': 'text-3w2e3DBc'}).find_all('p')

# 分词
sentences = []
words = jieba.cut(title.string.strip(), cut_all=False)
sentence = "/" .join(words)
sentence = re.split(r'\W+', sentence)
words = [word for word in sentence if len(word) > 0]
sentences.append(words)

for content in contents:
    words = jieba.cut(content.string.strip(), cut_all=False)
    sentence = "/" .join(words)
    sentence = re.split(r'\W+', sentence)
    words = [word for word in sentence if len(word) > 0]
    sentences.append(words)

# Word2Vec训练
model = Word2Vec(sentences=sentences, vector_size=50, window=2, min_count=1, workers=4)
model.save("word2vec.model")
model.train(sentences, total_examples=model.corpus_count, epochs=30) # 增大epoches
sims = model.wv.most_similar('中国', topn=10)  # get other similar words

# 输出
with open("word_vector.txt", "w") as f:
    for word in model.wv.index_to_key:
        vec = list(model.wv[word])
        vec = [str(x) for x in vec]
        f.write("%s: " %(word))
        f.write(", ".join(vec))
        f.write("\n")

with open("top10_words.txt", "w") as f:
    for pair in sims:
        f.write("%s: " %(pair[0]))
        f.write("%s" %(str(pair[1])))
        f.write("\n")

