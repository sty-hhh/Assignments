import random
import math
import numpy as np

n = 100
nodes_list = [5, 10, 20, 30, 40, 50, 60, 70, 80, 100]

# 随机获取一个点，判断是否在函数积分中
def getOneNode():    
    x = random.random()
    y = random.random()
    return y <= math.pow(x, 3)

# 蒙特卡洛法计算积分
def calculate(nodes):    
    t = 0
    for _ in range(nodes):
        if getOneNode():
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