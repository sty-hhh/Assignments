import numpy as np
import cv2
from sklearn.decomposition import PCA
import matplotlib.pylab as plt

# 将144d向量转为图像格式
def Back(data, height, width):
    res = np.zeros((height, width), dtype= np.int)
    index = 0
    for i in range(0, height, 12):
        for j in range(0, width, 12):
            res[i:i+12, j:j+12] = data[index].reshape(12, 12)
            index += 1
    return res

# 将图像大小处理为12的倍数
img = cv2.imread("../data/imgs/174.png", cv2.IMREAD_GRAYSCALE)
img = img[0:img.shape[0]//12*12, 0:img.shape[1]//12*12]
img = np.array(img).astype(int)
cv2.imwrite("../result/4/144d.png", img) 

# 取每个12*12patch为144d向量
for i in range(0, img.shape[0], 12):
    for j in range(0, img.shape[1], 12):
        temp = img[i:i+12, j:j+12].reshape(1,-1)
        if i == 0 and j == 0:
            data = temp
        else:
            data = np.concatenate((data, temp), axis=0)

m = np.mean(data, axis=0)       # 均值
c = data - m                    # 减去均值
covMat = np.cov(c, rowvar=0)    # 协方差矩阵
eigVals, eigVectors = np.linalg.eig(np.mat(covMat)) # 特征值和特征向量
eigValInd = np.argsort(-eigVals)    # 特征值由大到小排序
eigValInd = eigValInd[:16]          # 取前16个特征值的序号  
Vectors = eigVectors[:, eigValInd]  # 取前16个特征向量 
Vectors = Vectors.T

# 特征向量可视化
for i, vec in enumerate(Vectors):
    fig = plt.imshow(vec.reshape(12, 12), origin='upper')
    fig.set_cmap('gray_r')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.savefig("../result/4/eigVectors/"+str(i)+".png", bbox_inches='tight', pad_inches=-0.05)

# PCA降维
dimension = [60, 16, 6]
for i in dimension: 
    pca = PCA(n_components = i)
    x = pca.fit_transform(data)
    x = pca.inverse_transform(x)
    x = Back(x, img.shape[0], img.shape[1])
    cv2.imwrite("../result/4/"+str(i)+"d.png", x)