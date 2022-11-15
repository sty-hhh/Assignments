import numpy as np
import pandas as pd
import time
import os
from nltk.tokenize.toktok import ToktokTokenizer
from gensim.models import Word2Vec

tokenizer=ToktokTokenizer()
start = time.time()


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
print(train_corpus[:2])
print(len(train_corpus))
print(type(train_corpus))
# word2vec训练
model = Word2Vec(sentences=train_corpus,vector_size=100, min_count=5, workers = 4, window = 2)
model.save('word2vec.model')
model.train(train_corpus, total_examples=model.corpus_count, epochs=20)
model = Word2Vec.load('word2vec.model')
end = time.time()
print('Running time: {:.4f}s'.format(end-start))

start = time.time()
# 将词语vector转为句子vector
def make_sentence(corpus, model, num_features):
    vectors = []
    index2word_set = set(model.wv.index_to_key)
    for line in corpus:
        # Pre-initialising empty numpy array for speed
        featureVec = np.zeros(num_features,dtype='float32')
        nwords = 0
        for word in line:
            if word in index2word_set:
                #print('Found Word')
                nwords = nwords + 1
                featureVec = np.add(featureVec,model.wv[word])
    
        # Dividing the result by number of words to get average
        featureVec = np.divide(featureVec, nwords)
        vectors.append(list(featureVec))
    return np.array(vectors)


print(len(train_corpus[0]))
train_vectors = make_sentence(train_corpus, model, model.vector_size)
valid_vectors = make_sentence(valid_corpus, model, model.vector_size)
test_vectors = make_sentence(test_corpus, model, model.vector_size)

end = time.time()
print('Running time: {:.4f}s'.format(end-start))

print(test_vectors.dtype)


# 保存numpy数组
np.save('w2v/train_vectors.npy', train_vectors)
np.save('w2v/valid_vectors.npy', valid_vectors)
np.save('w2v/test_vectors.npy', test_vectors)
np.save('w2v/train_labels.npy', train_labels)
np.save('w2v/valid_labels.npy', valid_labels)
np.save('w2v/test_labels.npy', test_labels)