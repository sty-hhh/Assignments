# README

## 文件说明

RNN1.py：不用nn.Embedding的LSTM模型（用于TF、TF-IDF、word2vec词向量取平均）

RNN2.py：使用nn.Embedding的LSTM模型（用于word2vec词向量nn.Embedding）

RNN3.py：使用nn.Embedding的LSTM模型+Attention机制（用于word2vec词向量nn.Embedding）

text_clean.py：数据清洗和文本预处理

tf.py：生成TF矩阵

tfidf.py：生成TF-IDF矩阵

weight.py：用word2vec模型生成词嵌入矩阵

word2vec.py：生成word2vec模型的代码

## 运行方法

将IMDB Dataset.csv放至代码同一文件夹下，先进行数据清洗和文本预处理

~~~powershell
python text_clean.py
~~~

然后对于不同矩阵和模型：

TF

~~~powershell
python tf.py
python RNN1.py
~~~

TF-IDF

~~~powershell
python tfidf.py
python RNN1.py
~~~

word2vec词向量取平均

~~~powershell
python word2vec.py
python RNN1.py
~~~

word2vec词向量使用nn.Embedding

~~~powershell
python word2vec.py
python weight.py
python RNN2.py
~~~

word2vec词向量使用nn.Embedding+Attention机制

~~~powershell
python word2vec.py
python weight.py
python RNN3.py
~~~

