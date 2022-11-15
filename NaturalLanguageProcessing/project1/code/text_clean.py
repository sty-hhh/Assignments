#Load the libraries
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
import re
from nltk.tokenize.toktok import ToktokTokenizer
import time
import os

start = time.time()
# 读取文件
def read_file(filepath):
    df = pd.read_csv(filepath)
    data_set = list(df['review'])
    label_set = []
    for label in df['sentiment']:
        if label=='positive':
            label_set.append(1)
        else:
            label_set.append(0)
    data = pd.DataFrame({'review': data_set, 'sentiment': label_set})
    return data

data = read_file('IMDB Dataset.csv')

# 去除html标签和url
def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

data['review']=data['review'].apply(strip_html)

# 去除符号
def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text)

data['review']=data['review'].apply(remove_between_square_brackets)

#Tokenization of text
tokenizer=ToktokTokenizer()
# 去除脏数据
def judge_pure_english(word):
    return all(((ord(c)>64 and ord(c)<91) or (ord(c)>96 and ord(c)<128)) for c in word)

# 去除特殊符号
def remove_special_characters(text):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    filtered_tokens = [token.lower() for token in tokens if judge_pure_english(token)]
    filtered_text = ' '.join(filtered_tokens)    
    return filtered_text

data['review']=data['review'].apply(remove_special_characters)
print('预处理')
print(data['review'][11])


#Setting English stopwords
stopwords = nltk.corpus.stopwords.words('english')
specific_sw = ['br', 'movie', 'film', 'im']
print('停用词')
print(stopwords) 
stop = set(stopwords+specific_sw)

#removing the stopwords
def remove_stopwords(text):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    filtered_tokens = [token.lower() for token in tokens if token.lower()  not in stop]
    filtered_text = ' '.join(filtered_tokens)    
    return filtered_text
#Apply function on review column
data['review']=data['review'].apply(remove_stopwords)
print('去除停用词')
print(data['review'][3])

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
# 获取单词的词性
def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def lemmatization(text):
    wnl = WordNetLemmatizer()
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    tagged_sent = nltk.pos_tag(tokens)
    lemmas_sent = []
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
        lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos)) # 词形还原
    sentence = ' '.join(lemmas_sent)
    return sentence

start = time.time()
data['review']=data['review'].apply(lemmatization)
print('词形还原')
print(data['review'][12])

end = time.time()
print("Running time: {:.4f}s".format(end-start))


# 词干化
def stemming(text):
    ps = PorterStemmer()
    text = ' '.join([ps.stem(word) for word in text.split()])
    return text
#Apply function on review column
data['review']=data['review'].apply(stemming)
print('词干化')
print(data['review'][12])



end = time.time()
print("Running time: {:.4f}s".format(end-start))

data.to_csv('clean_text.csv', index=None, encoding='utf8')


# 词形还原后prepared动词形容词不对劲，再词干提取


