#encoding = UTF-8#
import numpy as np
import pandas as pd
#激活函数
def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def relu(z):
    return np.maximum(0, z)


def Tanh(z):
    return np.tanh(z)


def LeakyRelu(z):
    return np.maximum(0.01*z, z)


def der_sigmoid(z):
    return sigmoid(z)*(1-sigmoid(z))


def der_relu(z):
    ans = z.copy()
    ans[z > 0] = 1
    ans[z <= 0] = 0
    return ans


def der_Tanh(z):
    return 1-Tanh(z)*Tanh(z)


def der_LeakyRelu(z):
    ans = z.copy()
    ans[z > 0] = 1
    ans[z <= 0] = 0.01
    return ans

#X--训练集数据 Y--训练集标签 learning_rate:学习率 iterations:迭代次数 layers_dismension:各层节点数
def NeuralNetwork(X, Y, learning_rate, iterations, layers_dismension):
    lamd = 0.01#L2正则化系数
    m = X.shape[1]
    L = len(layers_dismension)
    W = [i for i in range(L)]
    b = [i for i in range(L)]
    for i in range(1, L):
        if i < L-1:
            W[i] = np.random.randn(
                layers_dismension[i], layers_dismension[i-1]) * np.sqrt(2 / layers_dims[i - 1])
            '''He Normal初始化: 正态分布的均值为0,方差为sqrt( 2/fan_in )。 适用于relu/leakyrelu'''
            '''Xavier 正态分布的均值为0,方差为sqrt( 2/(fan_in + fan_out) )。 适用于tanh sigmoid '''
            '''权重不能初始化为0,导致隐藏层的节点的权重均相同,相当于一个神经元'''
        else:
            W[i] = np.random.randn(layers_dismension[i],
                                   layers_dismension[i-1])*0.01
        b[i] = np.zeros((layers_dismension[i], m))

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
                Output[j] = LeakyRelu(Input[j])
            else:
                Output[j] = sigmoid(Input[j])

        # 反向传播
        loss = -1/m * \
            (np.dot(np.log(Output[L-1]), Y.T) +
             np.dot(np.log(1-Output[L-1]), 1-Y.T))  # 交叉熵
        regular_cost = 0
        
        for j in range(1, L):
            regular_cost += np.sum(np.square(W[j]))*lamd/(2*m)  # L2正则化
        
        loss += regular_cost

        dOutput[L-1] = -1/m*(np.divide(Y, Output[L-1]) -
                             np.divide(1-Y, 1-Output[L-1]))
        for j in range(L-1, 0, -1):
            if j == L-1:  # sigmoid
                dInput[j] = dOutput[L-1]*der_sigmoid(Input[L-1])
            else:  # Relu
                dInput[j] = dOutput[j]*der_LeakyRelu(Input[j])
            dW[j] = np.dot(dInput[j], Output[j-1].T)+lamd/(2*m)
            db[j] = dInput[j]
            dOutput[j-1] = np.dot(W[j].T, dInput[j])
            W[j] = W[j]-learning_rate*dW[j]
            b[j] = b[j] - learning_rate*db[j]
        if i % 100 == 0:
            print("训练集上损失函数:%f"%loss[0])
        Loss.append(loss[0])
    return W, b


def Predict(W, b, layers_dims, test_X):#在测试集上进行预测
    for j in range(1, len(layers_dims)):
        b[j] = b[j][:, 0:len(test_X[0])]
    L = len(layers_dims)
    Output = [test_X, ]+[i for i in range(L-1)]
    Input = [i for i in range(L)]
    for j in range(1, L):#前向传播
        Input[j] = np.dot(W[j], Output[j-1])+b[j]
        if j < L-1:
            Output[j] = LeakyRelu(Input[j])
        else:
            Output[j] = sigmoid(Input[j])
    ans = []
    for j in range(len(Output[L-1][0])):
        if Output[L-1][0][j] <= 0.5:#负类
            ans.append(0)
        else:
            ans.append(1)
    return ans


train_vectors = np.load("code/classify/train_vectors.npy")
valid_vectors = np.load("code/classify/valid_vectors.npy")
valid_labels = np.load("code/classify/valid_labels.npy")
train_labels = np.load("code/classify/train_labels.npy")
test_vectors = np.load("code/classify/test_vectors.npy")
print(train_vectors.shape)
print(valid_vectors.shape)
print(train_labels.shape)
print(valid_labels.shape)
print(test_vectors.shape)
n0 = train_vectors.shape[1]
n1 = 50
n3 = 1
layers_dims = [n0, n1, n3]
Loss = []
W, b = NeuralNetwork(train_vectors.T, train_labels,
                      0.01, 5000, layers_dims)
res = Predict(W, b, layers_dims, valid_vectors.T)
count = 0
for i in range(len(res)):
    if res[i] == valid_labels[i]:
        count += 1
print("validset accuracy:%f" % (count/len(valid_labels)))
test_res = Predict(W, b, layers_dims, test_vectors.T)
dict = {'id': [i for i in range(8001, 9001)], 'is_humor': test_res}
df = pd.DataFrame(dict)
df = df.drop([0, 1])
df.to_csv('code/classify/classify_NN.csv')

