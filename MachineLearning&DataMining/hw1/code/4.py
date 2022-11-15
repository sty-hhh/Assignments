import random
import numpy as np

n = 100
nodes_list = [20, 200, 2000, 20000]

def calculate(num):
    p = 0
    for _ in range(num):
        s = np.zeros((7,7))
        x = 0
        y = 0
        while True:
            if x==6 and y==6:
                p += 1
                break
            s[x][y] += 1
            t = []
            if x-1>=0 and (s[x-1][y]<1 or s[x-1][y]<2 and x-1==3 and y==3): # 向左
                t.append(0)
            if x+1<=6 and (s[x+1][y]<1 or s[x+1][y]<2 and x+1==3 and y==3): # 向右
                t.append(1)
            if y-1>=0 and (s[x][y-1]<1 or s[x][y-1]<2 and y-1==3 and x==3): # 向下
                t.append(2)
            if y+1<=6 and (s[x][y+1]<1 or s[x][y+1]<2 and y+1==3 and x==3): # 向上
                t.append(3)
            if len(t)==0:
                break
            n = t[random.randint(0, len(t)-1)]
            if n == 0:
                x -= 1
            if n == 1:
                x += 1
            if n == 2:
                y -= 1
            if n == 3:
                y += 1
    return p/num

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