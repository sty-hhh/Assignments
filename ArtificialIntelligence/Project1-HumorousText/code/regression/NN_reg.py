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

def NeuralNetwork(X, Y, learning_rate, iterations, layers_dismension):
    lamd = 0.01#L2正则化系数
    m = X.shape[1]
    L = len(layers_dismension)
    W = [i for i in range(L)]
    b = [i for i in range(L)]
    for i in range(1, L):#初始化参数
        if i < L-1:
            W[i] = np.random.randn(
                layers_dismension[i], layers_dismension[i-1]) * np.sqrt(2 / layers_dismension[i - 1])
        else:
            W[i] = np.random.randn(layers_dismension[i],
                                   layers_dismension[i-1])*0.01
        b[i] = np.zeros((layers_dismension[i], 1))

    Output = [X, ]+[i for i in range(L-1)]
    Input = [i for i in range(L)]

    dOutput = [i for i in range(L)]
    dInput = [i for i in range(L)]
    dW = [i for i in range(L)]
    db = [i for i in range(L)]

    for i in range(iterations):
        # 前向传播
        for j in range(1, L):
            Input[j] = np.dot(W[j], Output[j-1])+b[j]
            if j < L-1:
                Output[j] = relu(Input[j])#输出层改为Relu
            else:
                Output[j] = 4*sigmoid(Input[j])

        # 反向传播
        loss = 1/(2*m)*np.sum(np.square(Y-Output[L-1]))  # 均方差函数用于回归
        regular_cost = 0
        for j in range(1,L):
            regular_cost += np.sum(np.square(W[j]))*lamd/(2*m) #正则化
        loss += regular_cost
        dOutput[L-1] = 1/m*(Output[L-1]-Y)
        for j in range(L-1, 0, -1):
            if j < L-1:
                dInput[j] = dOutput[j]*der_relu(Input[j])
            else:
                dInput[j] = 4*dOutput[j]*der_sigmoid(Input[j])
            dW[j] = np.dot(dInput[j], Output[j-1].T)+lamd/m*W[j]
            db[j] = 1/m * np.sum(dInput[j], axis=1, keepdims=True)
            dOutput[j-1] = np.dot(W[j].T, dInput[j])
            W[j] = W[j]-learning_rate*dW[j]
            b[j] = b[j] - learning_rate*db[j]
        if i % 100 == 0:
            error = np.power(np.sum(np.square(Y-Output[L-1]))/m,0.5)
            print('训练集误差%f'%error)
    return W, b


def Predict(W, b, layers_dims, test_X):#在测试集上预测
    L = len(layers_dims)
    Output = [test_X, ]+[i for i in range(L-1)]
    Input = [i for i in range(L)]
    for j in range(1, L):
        Input[j] = np.dot(W[j], Output[j-1])+b[j]
        if j < L-1:
            Output[j] = relu(Input[j])
        else:
            Output[j] = 4*sigmoid(Input[j])
    ans = []
    for j in range(len(Output[L-1][0])):
        ans.append(Output[L-1][0][j])
    return ans

if __name__ == "__main__":
    train_vectors = np.load("code/regression/train_vectors.npy")
    valid_vectors = np.load("code/regression/valid_vectors.npy")
    valid_rating = np.load("code/regression/valid_rating.npy")
    train_rating = np.load("code/regression/train_rating.npy")
    test_id = np.load("code/regression/test_id.npy")
    test_vectors = np.load("code/regression/test_vectors.npy")
    print(train_vectors.shape)
    print(valid_vectors.shape)
    print(train_rating.shape)
    print(test_id.shape)
    print(test_vectors.shape)
    print(valid_rating.shape)
    n0 = train_vectors.shape[1]
    n1 = 50
    n2 = 7
    n3 = 1
    layers_dims = [n0, n1,n2,n3]#神经网络各层节点数
    W, b = NeuralNetwork(train_vectors.T, train_rating, 0.01, 8000, layers_dims)
    res = Predict(W, b, layers_dims,valid_vectors.T)
    loss = np.power(np.sum(np.square(np.asarray(res)-np.asarray(valid_rating)))/len(valid_rating),0.5)
    print("验证集上误差:")
    print(loss)
    test_res = Predict(W,b,layers_dims,test_vectors.T)
    dict = {'id':test_id,'humor_rating':test_res}
    df = pd.DataFrame(dict)
    df.to_csv('code/regression/regressNN.csv',index=None, encoding='utf8')
