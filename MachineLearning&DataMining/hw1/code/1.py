import random
import math
import numpy as np

n = 100
nodes_list = [20, 50, 100, 200, 300, 500, 1000, 5000]

# 随机获取一个点，并判断是否在 1/4 个圆上
def getOneNode():    
    x = random.random()
    y = random.random()
    return math.pow(x, 2)+math.pow(y, 2) <= 1

# 蒙特卡洛法计算pi值
def getPi(nodes):    
    circle = 0
    for _ in range(nodes):
        if getOneNode():
            circle += 1
    return 4*(circle/nodes)

# 计算均值和方差
for nodes in nodes_list:
    s = np.empty(n)
    for i in range(n):
        s[i] = getPi(nodes)
    mean = np.mean(s)
    var = np.var(s)
    print(nodes)
    print('mean: ', mean)
    print('var: ', var)