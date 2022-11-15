#%%
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

# start = time.time()
# 读取文件
train1 = pd.read_csv('text/comp/train.csv')
valid1 = pd.read_csv('text/comp/valid.csv')
test1 = pd.read_csv('text/comp/test.csv')
train2 = pd.read_csv('text/rec/train.csv')
valid2 = pd.read_csv('text/rec/valid.csv')
test2 = pd.read_csv('text/rec/test.csv')
train3 = pd.read_csv('text/sci/train.csv')
valid3 = pd.read_csv('text/sci/valid.csv')
test3 = pd.read_csv('text/sci/test.csv')
train4 = pd.read_csv('text/talk/train.csv')
valid4 = pd.read_csv('text/talk/valid.csv')
test4 = pd.read_csv('text/talk/test.csv')

print(train1['text'][10])

# 去除html标签和url
def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

train1['text']=train1['text'].apply(strip_html)
valid1['text']=valid1['text'].apply(strip_html)
test1['text']=test1['text'].apply(strip_html)
train2['text']=train2['text'].apply(strip_html)
valid2['text']=valid2['text'].apply(strip_html)
test2['text']=test2['text'].apply(strip_html)
train3['text']=train3['text'].apply(strip_html)
valid3['text']=valid3['text'].apply(strip_html)
test3['text']=test3['text'].apply(strip_html)
train4['text']=train4['text'].apply(strip_html)
valid4['text']=valid4['text'].apply(strip_html)
test4['text']=test4['text'].apply(strip_html)

#%%
# 去除符号
def remove_between_square_brackets(text):
    # return re.sub('[\n]\'', '', text)
    return re.sub('\[[^]]*\]', '', text)

train1['text']=train1['text'].apply(remove_between_square_brackets)
valid1['text']=valid1['text'].apply(remove_between_square_brackets)
test1['text']=test1['text'].apply(remove_between_square_brackets)
train2['text']=train2['text'].apply(remove_between_square_brackets)
valid2['text']=valid2['text'].apply(remove_between_square_brackets)
test2['text']=test2['text'].apply(remove_between_square_brackets)
train3['text']=train3['text'].apply(remove_between_square_brackets)
valid3['text']=valid3['text'].apply(remove_between_square_brackets)
test3['text']=test3['text'].apply(remove_between_square_brackets)
train4['text']=train4['text'].apply(remove_between_square_brackets)
valid4['text']=valid4['text'].apply(remove_between_square_brackets)
test4['text']=test4['text'].apply(remove_between_square_brackets)





#%%
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

train1['text']=train1['text'].apply(remove_special_characters)
valid1['text']=valid1['text'].apply(remove_special_characters)
test1['text']=test1['text'].apply(remove_special_characters)
train2['text']=train2['text'].apply(remove_special_characters)
valid2['text']=valid2['text'].apply(remove_special_characters)
test2['text']=test2['text'].apply(remove_special_characters)
train3['text']=train3['text'].apply(remove_special_characters)
valid3['text']=valid3['text'].apply(remove_special_characters)
test3['text']=test3['text'].apply(remove_special_characters)
train4['text']=train4['text'].apply(remove_special_characters)
valid4['text']=valid4['text'].apply(remove_special_characters)
test4['text']=test4['text'].apply(remove_special_characters)
print('预处理')
print(train1['text'][10])

#%%
#Setting English stopwords
stopwords = nltk.corpus.stopwords.words('english')
# stopwords = []
specific_sw = ['br', 'b', 'im','subject','re']
print('停用词')
# print(stopwords) 
stop = set(stopwords+specific_sw)

#removing the stopwords
def remove_stopwords(text):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    filtered_tokens = [token.lower() for token in tokens if token.lower()  not in stop]
    filtered_text = ' '.join(filtered_tokens)    
    return filtered_text
#Apply function on review column
train1['text']=train1['text'].apply(remove_stopwords)
valid1['text']=valid1['text'].apply(remove_stopwords)
test1['text']=test1['text'].apply(remove_stopwords)
train2['text']=train2['text'].apply(remove_stopwords)
valid2['text']=valid2['text'].apply(remove_stopwords)
test2['text']=test2['text'].apply(remove_stopwords)
train3['text']=train3['text'].apply(remove_stopwords)
valid3['text']=valid3['text'].apply(remove_stopwords)
test3['text']=test3['text'].apply(remove_stopwords)
train4['text']=train4['text'].apply(remove_stopwords)
valid4['text']=valid4['text'].apply(remove_stopwords)
test4['text']=test4['text'].apply(remove_stopwords)
print('去除停用词')
print(train1['text'][11])

#%%
# from nltk.corpus import wordnet
# from nltk.stem import WordNetLemmatizer
# # 获取单词的词性
# def get_wordnet_pos(tag):
#     if tag.startswith('J'):
#         return wordnet.ADJ
#     elif tag.startswith('V'):
#         return wordnet.VERB
#     elif tag.startswith('N'):
#         return wordnet.NOUN
#     elif tag.startswith('R'):
#         return wordnet.ADV
#     else:
#         return None

# def lemmatization(text):
#     wnl = WordNetLemmatizer()
#     tokens = tokenizer.tokenize(text)
#     tokens = [token.strip() for token in tokens]
#     tagged_sent = nltk.pos_tag(tokens)
#     lemmas_sent = []
#     for tag in tagged_sent:
#         wordnet_pos = get_wordnet_pos(tag[1]) or wordnet.NOUN
#         lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos)) # 词形还原
#     sentence = ' '.join(lemmas_sent)
#     return sentence

# start = time.time()
# train1['text']=train1['text'].apply(lemmatization)
# valid1['text']=valid1['text'].apply(lemmatization)
# test1['text']=test1['text'].apply(lemmatization)
# train2['text']=train2['text'].apply(lemmatization)
# valid2['text']=valid2['text'].apply(lemmatization)
# test2['text']=test2['text'].apply(lemmatization)
# train3['text']=train3['text'].apply(lemmatization)
# valid3['text']=valid3['text'].apply(lemmatization)
# test3['text']=test3['text'].apply(lemmatization)
# train4['text']=train4['text'].apply(lemmatization)
# valid4['text']=valid4['text'].apply(lemmatization)
# test4['text']=test4['text'].apply(lemmatization)
# print('词形还原')
# print(train1['text'][12])

# end = time.time()
# print(train1['text'][11])
# print(train1['labels'][11])
# print("Running time: {:.4f}s".format(end-start))

#%%
# 词干化
# def stemming(text):
#     ps = PorterStemmer()
#     text = ' '.join([ps.stem(word) for word in text.split()])
#     return text
# #Apply function on review column
# train1['text']=train1['text'].apply(stemming)
# valid1['text']=valid1['text'].apply(stemming)
# test1['text']=test1['text'].apply(stemming)
# train2['text']=train2['text'].apply(stemming)
# valid2['text']=valid2['text'].apply(stemming)
# test2['text']=test2['text'].apply(stemming)
# train3['text']=train3['text'].apply(stemming)
# valid3['text']=valid3['text'].apply(stemming)
# test3['text']=test3['text'].apply(stemming)
# train4['text']=train4['text'].apply(stemming)
# valid4['text']=valid4['text'].apply(stemming)
# test4['text']=test4['text'].apply(stemming)
# print('词干化')

#%%
print(train1['text'][11])
print()
print(train1['text'][12])


train1.to_csv('data/comp/train.csv', index=None, encoding='utf8')
valid1.to_csv('data/comp/valid.csv', index=None, encoding='utf8')
test1.to_csv('data/comp/test.csv', index=None, encoding='utf8')
train2.to_csv('data/rec/train.csv', index=None, encoding='utf8')
valid2.to_csv('data/rec/valid.csv', index=None, encoding='utf8')
test2.to_csv('data/rec/test.csv', index=None, encoding='utf8')
train3.to_csv('data/sci/train.csv', index=None, encoding='utf8')
valid3.to_csv('data/sci/valid.csv', index=None, encoding='utf8')
test3.to_csv('data/sci/test.csv', index=None, encoding='utf8')
train4.to_csv('data/talk/train.csv', index=None, encoding='utf8')
valid4.to_csv('data/talk/valid.csv', index=None, encoding='utf8')
test4.to_csv('data/talk/test.csv', index=None, encoding='utf8')




