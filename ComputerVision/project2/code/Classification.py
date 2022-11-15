import numpy as np
import cv2
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from Segmentation import apply

# RGB直方图
def rgb_histogram(img):
    cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)
    img = img.reshape(-1, 3)
    h = np.zeros((8, 8, 8), dtype = np.float)
    for i in range(img.shape[0]):
        b, g, r = np.floor(img[i] / 32).astype(int)
        h[r][g][b] += 1
    h = h.reshape(-1) / (img.shape[0])
    return h

# 处理特征
def process(img_path, gt_path, img_set):
    for i in range(len(img_set)):
        print("Processing img", i, "...")
        img = cv2.imread(img_path + "/" + str(img_set[i]) + ".png")
        gt = cv2.imread(gt_path + "/" + str(img_set[i]) + ".png")
        _, num, front, clusters = apply(img, gt, "", 70, 50, 50, 117)
        h = rgb_histogram(img)
        features = np.zeros((num, 2 * 512))
        for j in range(num):
            img = img.reshape(-1, 3)
            features[j][:512] = rgb_histogram(img[clusters[j]])
            features[j][512:] = h
        if i == 0:
            labels = front
            data = features
        else:
            labels += front
            data = np.concatenate((data, features), axis=0)
    return data, labels

train_set, test_set = [], []
for i in range(1, 1001):
    if i % 100 == 74:
        test_set.append(i)
    else:
        train_set.append(i)
train_set = np.random.choice(train_set, 200, replace=False)
train, train_labels = process("../data/imgs", "../data/gt", train_set)
test, test_labels = process("../data/imgs", "../data/gt", test_set)
# PCA降维
pca = PCA(n_components = 20)
train, test = pca.fit_transform(train), pca.transform(test)
# KMeans聚类
cluster = KMeans(n_clusters=50).fit(train)
center = cluster.cluster_centers_
train = np.concatenate((np.dot(train, center.T), train), axis = 1)
test = np.concatenate((np.dot(test, center.T), test), axis = 1)

# 随机森林分类
model = RandomForestClassifier(n_estimators=100)
model.fit(train, train_labels)
print("RandomForest")
print("train acc : ", metrics.accuracy_score(train_labels, model.predict(train)))
print("test acc : ", metrics.accuracy_score(test_labels, model.predict(test)))
