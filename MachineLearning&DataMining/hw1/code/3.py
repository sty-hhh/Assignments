import random
import math
import numpy as np

n = 100
nodes_list = [10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 500]

# 随机获取一个点，计算期望积分
def getOneNode():    
    x = random.uniform(2, 4)
    y = random.uniform(-1, 1)
    a = math.pow(y, 2)*math.exp(-math.pow(y, 2))
    b = math.pow(x, 4)*math.exp(-math.pow(x, 2))
    c = x*math.exp(-math.pow(x, 2))
    z = (a+b)/c
    return z*4

# 蒙特卡洛法计算积分
def calculate(nodes):    
    t = 0
    tmp = 0
    for _ in range(nodes):
        t = getOneNode()
        tmp += t
    return tmp/nodes

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