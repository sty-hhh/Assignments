# README

## 实验环境

软件环境

- Ubuntu Linux 18.04
- Python 3.8.8
- Cuda compilation tools, release 9.1, V9.1.85

硬件环境

- Intel(R) Core(TM) i7-5930K CPU @ 3.50GHz
- GeForce GTX TITAN X/PCle/SSE2  

## 代码说明及运行方法

- text.py 用于将20news-18828中的4个数据集的4个类别均匀划分，分别得到4个数据集的训练集和测试集，在与20news-18828同一目录下


~~~powershell
python test.py	
~~~

- clean.py用于文本处理（脏数据清洗、分词、统一大小写、去除停用词）

~~~powershell
python clean.py	
~~~

- weight.py用于加载预训练词向量和句子的长度统一，需要先下载[glove.6B预训练词向量](http://nlp.stanford.edu/data/glove.6B.zip)，在同一目录运行

~~~powershell
python weight.py	
~~~

- model.py用于训练测试CNN和RNN在单任务中的准确率，在代码中选择不同的模型和数据集可测得对应的结果

~~~powershell
python model.py	
~~~

- baseline.py用于模型在4个任务上依次训练，不使用任何抗遗忘方法，得到结果是模型下界

~~~powershell
python baseline.py	
~~~

- ewc.py使用EWC方法在4个任务上依次训练再依次测试

~~~powershell
python ewc.py	
~~~

- mas.py使用MAS方法在4个任务上依次训练再依次测试

~~~powershell
python mas.py	
~~~

- si.py使用SI方法在4个任务上依次训练再依次测试

~~~powershell
python si.py	
~~~

- plot.py用于将所有测试的结果画图，得到所有方法的准确率。每种方法分别实验5次，用于衡量模型稳定性

~~~powershell
python plot.py	
~~~







