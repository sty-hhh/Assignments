import matplotlib.pyplot as plt

# 完整数据
# p = [1, 1, 2/3, 0.75, 4/5, 5/6, 5/7, 6/8, 6/9, 7/10]
# r = [1/7, 2/7, 2/7, 3/7, 4/7, 5/7, 5/7, 6/7, 6/7, 1]

# 1、4、7、10的数据
p = [1, 0.75, 5/7, 7/10]
r = [1/7, 3/7, 5/7, 1]

plt.plot(r, p)  
plt.title("Precision-Recall Curve") 
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.tick_params(axis='both')
plt.show()