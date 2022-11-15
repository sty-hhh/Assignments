import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

train = np.array(pd.read_table('dataForTrainingLinear.txt',sep=' ',header=None))
test  = np.array(pd.read_table('dataForTestingLinear.txt',sep=' ',header=None))

def LinearRegression(lr=0.00015, w0=0, w1=0, w2=0, iterations=1500000, 
                     interval=100000, random_num=0):
    train_errors = []  
    test_errors = []  
    iteration_list = []  
    for iteration in range(1, iterations+1):
        sum_0, sum_1, sum_2 = 0, 0, 0
        if (random_num == 0):
            for i in range(len(train)):
                y = w0 + w1 * train[i][0] + w2 * train[i][1]  
                sum_0 += (y - train[i][2])
                sum_1 += (y - train[i][2]) * train[i][0]
                sum_2 += (y - train[i][2]) * train[i][1]
        else:
            for _ in range(random_num):
                index = random.randint(0, len(train) - 1)
                y = w0 + w1 * train[index][0] + w2 * train[index][1]  
                sum_0 += (y - train[index][2])
                sum_1 += (y - train[index][2]) * train[index][0]
                sum_2 += (y - train[index][2]) * train[index][1]

        w0 = w0 - lr * (sum_0 / (len(train) if (random_num == 0) else random_num))
        w1 = w1 - lr * (sum_1 / (len(train) if (random_num == 0) else random_num))
        w2 = w2 - lr * (sum_2 / (len(train) if (random_num == 0) else random_num))

        if (iteration % interval == 0):
            iteration_list.append(iteration)
            e1 = []
            for i in range(len(train)):
                y = w0+w1*train[i][0]+w2*train[i][1]  
                e1.append(y)
            e = np.sum(np.square(e1-train[:, 2]))/len(train)
            train_errors.append(e)
            e2 = []
            for i in range(len(test)):
                y = w0+w1*test[i][0]+w2*test[i][1] 
                e2.append(y)
            e = np.sum(np.square(e2-test[:, 2]))/len(test)
            test_errors.append(e)
    return iteration_list, train_errors, test_errors

iteration_list, train_errors, test_errors = \
    LinearRegression(lr=0.00015, iterations=20000, interval=2000, random_num=0)

plt.figure()
plt.plot(iteration_list, train_errors, "o-", c="r", label="train")
plt.plot(iteration_list, test_errors, "*-", c="b", label="test")
plt.xlabel("Iterations")
plt.ylabel("MSE")
plt.legend()
plt.title("Linear Regression")
plt.show()
