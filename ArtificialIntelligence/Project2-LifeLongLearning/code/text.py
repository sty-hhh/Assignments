# %%
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

def read_file(files,label):
    docs = []
    labels = []
    for file in files:
        name = path + file
        with open(name, 'rb') as f:
            f.readline()
            doc = f.read().lstrip()
            docs.append(doc)
            labels.append(label)
    return docs,labels

def read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels):
    files = os.listdir(path)
    docs,labels = read_file(files,label)
    train_data += docs[:len(docs)*6//10]
    valid_data += docs[len(docs)*6//10:len(docs)*8//10]    
    test_data += docs[len(docs)*8//10:]  
    train_labels += labels[:len(docs)*6//10]
    valid_labels += labels[len(docs)*6//10:len(docs)*8//10]    
    test_labels += labels[len(docs)*8//10:] 
    return train_data,valid_data,test_data,train_labels,valid_labels,test_labels

train_data = []
valid_data = []    
test_data = []  
train_labels = []
valid_labels = []   
test_labels = [] 

path = '20news-18828/comp.graphics/'
label = 0
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

path = '20news-18828/comp.os.ms-windows.misc/'
label = 1
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/comp.sys.mac.hardware/'
label = 2
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/comp.windows.x/'
label = 3
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

train = pd.DataFrame({'text': train_data, 'labels': train_labels})
train.to_csv('text/comp/train.csv', index=None, encoding='utf8')
valid = pd.DataFrame({'text': valid_data, 'labels': valid_labels})
valid.to_csv('text/comp/valid.csv', index=None, encoding='utf8')
test = pd.DataFrame({'text': test_data, 'labels': test_labels})
test.to_csv('text/comp/test.csv', index=None, encoding='utf8')

train_data = []
valid_data = []    
test_data = []  
train_labels = []
valid_labels = []   
test_labels = [] 

path = '20news-18828/rec.autos/'
label = 0
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

path = '20news-18828/rec.motorcycles/'
label = 1
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/rec.sport.baseball/'
label = 2
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/rec.sport.hockey/'
label = 3
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

train = pd.DataFrame({'text': train_data, 'labels': train_labels})
train.to_csv('text/rec/train.csv', index=None, encoding='utf8')
valid = pd.DataFrame({'text': valid_data, 'labels': valid_labels})
valid.to_csv('text/rec/valid.csv', index=None, encoding='utf8')
test = pd.DataFrame({'text': test_data, 'labels': test_labels})
test.to_csv('text/rec/test.csv', index=None, encoding='utf8')

train_data = []
valid_data = []    
test_data = []  
train_labels = []
valid_labels = []   
test_labels = [] 

path = '20news-18828/sci.crypt/'
label = 0
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

path = '20news-18828/sci.electronics/'
label = 1
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/sci.med/'
label = 2
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/sci.space/'
label = 3
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

train = pd.DataFrame({'text': train_data, 'labels': train_labels})
train.to_csv('text/sci/train.csv', index=None, encoding='utf8')
valid = pd.DataFrame({'text': valid_data, 'labels': valid_labels})
valid.to_csv('text/sci/valid.csv', index=None, encoding='utf8')
test = pd.DataFrame({'text': test_data, 'labels': test_labels})
test.to_csv('text/sci/test.csv', index=None, encoding='utf8')

train_data = []
valid_data = []    
test_data = []  
train_labels = []
valid_labels = []   
test_labels = [] 

path = '20news-18828/talk.politics.guns/'
label = 0
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

path = '20news-18828/talk.politics.mideast/'
label = 1
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/talk.politics.misc/'
label = 2
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)
    
path = '20news-18828/talk.religion.misc/'
label = 3
train_data,valid_data,test_data,train_labels,valid_labels,test_labels = \
    read2(path, label,train_data,valid_data,test_data,train_labels,valid_labels,test_labels)

train = pd.DataFrame({'text': train_data, 'labels': train_labels})
train.to_csv('text/talk/train.csv', index=None, encoding='utf8')
valid = pd.DataFrame({'text': valid_data, 'labels': valid_labels})
valid.to_csv('text/talk/valid.csv', index=None, encoding='utf8')
test = pd.DataFrame({'text': test_data, 'labels': test_labels})
test.to_csv('text/talk/test.csv', index=None, encoding='utf8')
        
        
        





# %%
