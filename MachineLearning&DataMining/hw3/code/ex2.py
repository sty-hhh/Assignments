import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

train = np.array(pd.read_table('dataForTrainingLogistic.txt',sep=' ',header=None))
test  = np.array(pd.read_table('dataForTestingLogistic.txt',sep=' ',header=None))
k_list = [i for i in range(10, 401, 10)]

def Sigmoid(h):
    res = 1.0 / (1.0 + np.exp(-h))
    return res

def LogisticRegression(train, lr=0.00015, w=np.zeros(7), iterations=1500000, interval=100000, random_num=0):
    train_errors = [] 
    train_LCL = [] 
    test_errors = []  
    test_LCL = []  
    iteration_list = [] 

    for iteration in range(1, iterations+1):
        sum = np.zeros(7)
        if random_num == 0:
            for i in range(len(train)):
                h = w[0]
                for j in range(1, 7):
                    h += w[j] * train[i][j-1]
                sum[0] += train[i][6] - Sigmoid(h)
                for j in range(1, 7):
                    sum[j] += (train[i][6] - Sigmoid(h)) * train[i][j-1]
        else:
            for _ in range(random_num):
                i = random.randint(0, len(train)-1)
                h = w[0]
                for j in range(1, 7):
                    h += w[j] * train[i][j-1]
                sum[0] += train[i][6] - Sigmoid(h)
                for j in range(1, 7):
                    sum[j] += (train[i][6] - Sigmoid(h)) * train[i][j-1]
        for i in range(7):
            w[i] += lr * sum[i]

        if iteration % interval == 0:
            iteration_list.append(iteration)
            cnt = 0
            LCL = 0
            for i in range(len(train)):
                h = w[0]
                for j in range(1, 7):
                    h += w[j] * train[i][j-1]
                LCL += train[i][6] * np.log(Sigmoid(h)) + (1 - train[i][6]) * np.log(1 - Sigmoid(h))
                if np.abs(Sigmoid(h) - train[i][6]) < 0.5:
                    cnt += 1
            e = 1 - (1.0 / len(train)) * cnt
            train_errors.append(e)
            train_LCL.append(LCL)
            cnt = 0
            LCL = 0
            for i in range(len(test)):
                h = w[0]
                for j in range(1, 7):
                    h += w[j] * test[i][j-1]
                LCL += test[i][6] * np.log(Sigmoid(h)) + (1 - test[i][6]) * np.log(1 - Sigmoid(h))
                if np.abs(Sigmoid(h) - test[i][6]) < 0.5:
                    cnt += 1
            e = 1 - (1.0 / len(test)) * cnt
            test_errors.append(e)
            test_LCL.append(LCL)
    return iteration_list, train_errors, train_LCL, test_errors, test_LCL

iteration_list, train_errors, train_LCL, test_errors, test_LCL = \
    LogisticRegression(train, lr=0.00015, iterations=1000, interval=50, random_num=10)

# # (c)
# plt.figure()
# plt.plot(iteration_list, train_errors, "o-", c="r", label="train")
# plt.plot(iteration_list, test_errors, "*-", c="b", label="test")
# plt.xlabel("Iterations")
# plt.ylabel("Error Rate")
# plt.legend()
# plt.title("Logistic Regression")
# plt.show()

# # (e)
# plt.figure()
# plt.plot(iteration_list, train_LCL, "o-", c="r", label="train")
# plt.plot(iteration_list, test_LCL, "*-", c="b", label="test")
# plt.xlabel("Iterations")
# plt.ylabel("Value of the Objective Function")
# plt.legend()
# plt.title("Logistic Regression")
# plt.show()

# (f)
error1 = []
error2 = []
for k in k_list:
    index=random.sample(range(0, len(train)), k)
    t = [train[index[i]] for i in range(k)]
    iteration_list, train_errors, train_LCL, test_errors, test_LCL = \
        LogisticRegression(t, lr=0.00015, iterations=100, interval=100, random_num=1)
    error1.append(train_errors[0])
    error2.append(test_errors[0])
    
plt.figure()
plt.plot(k_list, error1, "o-", c="b", label="train")
plt.plot(k_list, error2, "*-", c="r", label="test")
plt.xlabel("k")
plt.ylabel("Error Rate")
plt.legend()
plt.title("Logistic Regression")
plt.show()
