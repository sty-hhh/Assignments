import random
import numpy as np

n = 100
nodes_list = [10, 20, 30, 40, 50, 60, 70, 80, 100, 200]

# 随机采样A
def getA():    
    a = random.random()
    return a<=0.85 

# 随机采样BC
def getBC():    
    b = random.random()
    c = random.random()
    return b<0.95 and c<0.90

# 蒙特卡洛法计算概率
def calculate(nodes):    
    t = 0
    for _ in range(nodes//2):
        if getA():
            t += 1
    for _ in range(nodes//2):
        if getBC():
            t += 1
    return t/nodes

# 计算均值和方差
for nodes in nodes_list:
    s = np.empty(n)
    for i in range(n):
        s[i] = calculate(nodes)
    mean = np.mean(s)
    var = np.var(s)
    print(nodes)
    print('mean: ', mean)
    print('var: ', var)