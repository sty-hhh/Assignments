#encoding = UTF-8
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#激活函数
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
    batch_size = 256#每一次取batch_size进行训练
    for i in range(1, L):
        if i < L-1:
            W[i] = np.random.randn(
                layers_dismension[i], layers_dismension[i-1])* np.sqrt(2 / layers_dims[i - 1]) 
                #He初始化
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
    for i in range(0, L):
        if i:
            Output[i] = np.zeros((layers_dismension[i], X.shape[1]))
        Input[i] = np.zeros((layers_dismension[i], X.shape[1]))
        dOutput[i] = np.zeros((layers_dismension[i], X.shape[1]))
        dInput[i] = np.zeros((layers_dismension[i], X.shape[1]))

    for i in range(iterations):
        batch_mask = np.random.choice(X.shape[1], batch_size,replace=False)
        # 前向传播
        for j in range(1, L):
            Input[j][:, batch_mask] = np.dot(W[j], Output[j-1][:, batch_mask])+b[j]
            if j < L-1:
                Output[j][:, batch_mask] = LeakyRelu(Input[j][:, batch_mask])
            else:
                Output[j][:, batch_mask] = sigmoid(Input[j][:, batch_mask])

        # 反向传播
        loss = -1/batch_size * (np.dot(np.log(Output[L-1][:, batch_mask]), Y[batch_mask].T) + np.dot(np.log(1-Output[L-1][:, batch_mask]), 1-Y[batch_mask].T))#交叉熵
        regular_cost = 0
        for j in range(1,L):
            regular_cost += np.sum(np.square(W[j]))*lamd/(2*batch_size) #正则化
        loss += regular_cost
        dOutput[L-1][:, batch_mask] = -1/batch_size*(np.divide(Y[batch_mask],Output[L-1][:, batch_mask]) - np.divide(1-Y[batch_mask],1-Output[L-1][:, batch_mask]))
        for j in range(L-1, 0, -1):
            if j == L-1:  # sigmoid
                dInput[j][:, batch_mask] = dOutput[L-1][:, batch_mask]*der_sigmoid(Input[L-1][:, batch_mask])
            else:  #leakyRelu
                dInput[j][:, batch_mask] = dOutput[j][:, batch_mask]*der_LeakyRelu(Input[j][:, batch_mask])
            dW[j] = np.dot(dInput[j][:, batch_mask], Output[j-1][:, batch_mask].T)+lamd/batch_size*W[j]
            db[j] = 1/batch_size* np.sum(dInput[j][:, batch_mask], axis=1, keepdims=True)
            dOutput[j-1][:, batch_mask] = np.dot(W[j].T, dInput[j][:, batch_mask])
            W[j] = W[j]-learning_rate*dW[j]
            b[j] = b[j] - learning_rate*db[j]
        if i % 100 == 0:
            print('训练集损失函数:%f'%loss[0])
        Loss.append(loss[0])
    return W, b


def Predict(W, b, layers_dims, test_X):
    L = len(layers_dims)
    Output = [test_X, ]+[i for i in range(L-1)]
    Input = [i for i in range(L)]
    for j in range(1, L):
        Input[j] = np.dot(W[j], Output[j-1])+b[j]
        if j < L-1:
            Output[j] = LeakyRelu(Input[j])
        else:
            Output[j] = sigmoid(Input[j])
    ans = []
    for j in range(len(Output[L-1][0])):
        if Output[L-1][0][j] <= 0.5:
            ans.append(0)
        else:
            ans.append(1)
    return ans

train_vectors = np.load("code/classify/train_vectors.npy")#5600*100
valid_vectors = np.load("code/classify/valid_vectors.npy")#2400*100
valid_labels = np.load("code/classify/valid_labels.npy")#5600*1
train_labels = np.load("code/classify/train_labels.npy")#2400*1
test_vectors = np.load("code/classify/test_vectors.npy")
print(train_vectors.shape)
print(valid_vectors.shape)
print(train_labels.shape)
print(valid_labels.shape)
n0 = train_vectors.shape[1]
n1 = 50
n2 = 1
layers_dims = [n0, n1,n2]#神经网络的各层节点数目
Loss = []
W, b = NeuralNetwork(train_vectors.T,train_labels, 0.01, 5000, layers_dims)
res = Predict(W, b, layers_dims,valid_vectors.T)
count = 0
for i in range(len(res)):#验证集上准确率
    if res[i] == valid_labels[i]:
        count+=1
print("validset accuracy:%f"%(count/len(valid_labels)))
test_res = Predict(W, b, layers_dims, test_vectors.T)
dict = {'id': [i for i in range(8001, 9001)], 'is_humor': test_res}
df = pd.DataFrame(dict)
df = df.drop([0, 1])
df.to_csv('code/classify/classify_NN.csv')