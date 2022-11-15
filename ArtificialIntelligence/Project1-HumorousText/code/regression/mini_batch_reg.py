#encoding=UTF-8
import numpy as np
import random
import math
import pandas as pd
import matplotlib.pyplot as plt

def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def relu(z):
    return np.maximum(0, z)

def Tanh(z):
    return np.tanh(z)

def LeakyRelu(z):
    return np.maximum(0.01*z,z)

def der_sigmoid(z):
    return sigmoid(z)*(1-sigmoid(z))

def der_relu(z):
    ans = z.copy()
    ans[z>0] = 1
    ans[z<=0] = 0
    return ans

def der_Tanh(z):
    return 1-Tanh(z)*Tanh(z)

def der_LeakyRelu(z):
    ans = z.copy()
    ans[z>0] = 1
    ans[z<=0] = 0.01
    return ans
Err = []
def NeuralNetwork(X, Y, learning_rate, iterations, layers_dismension,random_state):

    lamd = 0.01#L2正则化系数
    m = X.shape[1]
    L = len(layers_dismension)
    W = [i for i in range(L)]
    b = [i for i in range(L)]
    for i in range(1, L):
        random.seed(random_state+i)
        W[i] = np.random.randn(
                layers_dismension[i], layers_dismension[i-1]) * np.sqrt(2 / layers_dims[i - 1])#HE初始化
        b[i] = np.zeros((layers_dismension[i], 1))

    Output = [X, ]+[i for i in range(L-1)]
    Input = [i for i in range(L)]

    dOutput = [i for i in range(L)]
    dInput = [i for i in range(L)]
    dW = [i for i in range(L)]
    db = [i for i in range(L)]
    for i in range(0, L):
        if i:
            Output[i] = np.zeros((layers_dismension[i], X.shape[1]))
        Input[i] = np.zeros((layers_dismension[i], X.shape[1]))
        dOutput[i] = np.zeros((layers_dismension[i], X.shape[1]))
        dInput[i] = np.zeros((layers_dismension[i], X.shape[1]))

    batch_size = 256
    for i in range(iterations):
        random.seed(L+random_state+i)#设置随机种子
        batch_mask = np.random.choice(X.shape[1], batch_size,replace=False)#随机选择batch_size个数据
        # 前向传播
        for j in range(1, L):
            Input[j][:, batch_mask] = np.dot(W[j], Output[j-1][:, batch_mask])+b[j]  # b[j] boardcast
            Output[j][:, batch_mask] = LeakyRelu(Input[j][:, batch_mask])  # 输出层改为LeakyRelu
        # 反向传播
        loss = 1/(2*(batch_size))*np.sum(np.square(Y[batch_mask]-Output[L-1][:,batch_mask]))  # 均方差函数用于回归
        regular_cost = 0
        for j in range(1,L):
            regular_cost += np.sum(np.square(W[j]))*lamd/(2*(batch_size)) #正则化
        loss += regular_cost
        dOutput[L-1][:,batch_mask] = 1/(batch_size)*(Output[L-1][:,batch_mask]-Y[batch_mask])
        for j in range(L-1, 0, -1):#反向传播更新参数
            dInput[j][:, batch_mask] = dOutput[j][:, batch_mask]*der_LeakyRelu(Input[j][:, batch_mask])
            dW[j] = np.dot(dInput[j][:,batch_mask], Output[j-1][:,batch_mask].T)+lamd/(batch_size)*W[j]
            db[j] = 1/(batch_size) * np.sum(dInput[j][:,batch_mask], axis=1, keepdims=True)
            dOutput[j-1][:,batch_mask] = np.dot(W[j].T, dInput[j][:,batch_mask])
            W[j] = W[j]-learning_rate*dW[j]
            b[j] = b[j] - learning_rate*db[j]
        if i % 100 == 0:
            error = np.power(np.sum(np.square(Y[batch_mask]-Output[L-1][:,batch_mask]))/batch_size,0.5)
            print("训练集误差:%f"%error)
        Err.append(np.power(np.sum(np.square(Y-Output[L-1]))/m,0.5))
    return W, b


def Predict(W, b, layers_dims, test_X):#利用训练的模型在测试集上进行测试
    L = len(layers_dims)
    Output = [test_X, ]+[i for i in range(L-1)]
    Input = [i for i in range(L)]
    for j in range(1, L):
        Input[j] = np.dot(W[j], Output[j-1])+b[j]
        Output[j] = LeakyRelu(Input[j])
    ans = []
    for j in range(len(Output[L-1][0])):
        ans.append(Output[L-1][0][j])
    return ans


train_vectors = np.load("code/regression/train_vectors.npy")
valid_vectors = np.load("code/regression/valid_vectors.npy")
valid_rating = np.load("code/regression/valid_rating.npy")
train_rating = np.load("code/regression/train_rating.npy")
test_id = np.load("code/regression/test_id.npy")
test_vectors = np.load("code/regression/test_vectors.npy")
n0 = train_vectors.shape[1]
n1 = 50
n2 = 10
n3 = 1
layers_dims = [n0, n1,n2,n3]#神经网络各层节点数
W, b = NeuralNetwork(train_vectors.T, train_rating, 0.01, 8000, layers_dims,10000)
res = Predict(W, b, layers_dims,valid_vectors.T)
loss = math.sqrt(1/len(valid_rating)*np.sum(np.square(np.asarray(res)-np.asarray(valid_rating))))
print("验证集上误差:")
print(loss)
test_res = Predict(W,b,layers_dims,test_vectors.T)
dict = {'id':test_id,'humor_rating':test_res}
df = pd.DataFrame(dict)
df.to_csv('code/regression/regress_hhh.csv',index=None, encoding='utf8')

