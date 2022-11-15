import cv2
import os
import numpy as np
from random import random

# 加边
def add_edge(img, width, x1, y1, x2, y2):
    return (x1 * width + y1, x2 * width + y2, np.sqrt(np.sum((img[x1, y1] - img[x2, y2])**2)))

# 初始化每个点的八邻域边
def init_edges(img, height, width):
    edges = []
    for row in range(height):
        for col in range(width):
            if row > 0:
                edges.append(add_edge(img, width, row, col, row-1, col))
            if col > 0:
                edges.append(add_edge(img, width, row, col, row, col-1))
            if row > 0 and col > 0:
                edges.append(add_edge(img, width, row, col, row-1, col-1))
            if row > 0 and col < width-1:
                edges.append(add_edge(img, width, row, col, row-1, col+1))
    return edges

# 定义节点
class Node:
    def __init__(self, x):
        self.root = x
        self.id = 0
        self.size = 1

# 并查集
class Union_set:
    # 初始化
    def __init__(self, num):
        self.nodes = [Node(i) for i in range(num)]
        self.num = num
    # 查找根节点
    def locate_root(self, n):
        p = n
        while p != self.nodes[p].root:
            p = self.nodes[p].root
        self.nodes[n].root = p
        return p
    # 合并区域
    def merge(self, a, b):
        if self.nodes[a].id > self.nodes[b].id:
            self.nodes[b].root = a
            self.nodes[a].size = self.nodes[a].size + self.nodes[b].size
        else:
            self.nodes[a].root = b
            self.nodes[b].size = self.nodes[b].size + self.nodes[a].size
        if self.nodes[a].id == self.nodes[b].id:
            self.nodes[b].id = self.nodes[b].id + 1
        self.num = self.num - 1

# 图像分割
def segment(edges, num, max_cluster, min_cluester, min_size, k):
    while True: 
        node_set = Union_set(num)
        weight = lambda edge: edge[2]
        edges = sorted(edges, key=weight)
        w = [k for _ in range(num)]
        for edge in edges:
            r1 = node_set.locate_root(edge[0])
            r2 = node_set.locate_root(edge[1])
            min_w = min(w[r1], w[r2])
            if r1 != r2 and weight(edge) < min_w:
                node_set.merge(r1, r2)
                r = node_set.locate_root(r1)
                w[r] = weight(edge) + (k / node_set.nodes[r].size)
        for edge in edges:
            r1 = node_set.locate_root(edge[0])
            r2 = node_set.locate_root(edge[1])
            if r1 != r2 and (node_set.nodes[r1].size < min_size or node_set.nodes[r2].size < min_size):
                node_set.merge(r1, r2)
        if node_set.num > max_cluster:
            k += 10
        elif node_set.num < min_cluester:
            k -= 10   
        else:
            break
    return node_set

# 计算IOU并生成分割图和前景图
def compute(node_set, img, gt, size):
    num = size[0] * size[1]
    front = [0] * num
    front_cluster = [0] * num
    for i in range(num):
        root = node_set.locate_root(i)
        if gt[int(i/size[1]), int(i%size[1]), 0] != 0:
            front[root] = front[root] + 1
        else:
            front[root] = front[root] - 1
    for i in range(num):
        if node_set.locate_root(i) == i and front[i] >= 0:
            front_cluster[i] = 1
    I, U = 0, 0
    for i in range(num):
        root = node_set.locate_root(i)
        if front_cluster[root] and gt[int(i/size[1]), int(i%size[1]), 0] != 0:
            I += 1
        if front_cluster[root] or gt[int(i/size[1]), int(i%size[1]), 0] != 0:
            U += 1
    # 生成分割图
    new_img = np.copy(img).reshape(-1,3)
    random_color = lambda: (int(random()*256), int(random()*256), int(random()*256))
    colors = [random_color() for _ in range(new_img.shape[0])]
    for idx in range(new_img.shape[0]):
        comp = node_set.locate_root(idx)
        new_img[idx] = colors[comp]
    new_img = new_img.reshape(img.shape)  
    # 生成前景图
    new_gt = np.zeros(gt.shape, dtype = np.int)
    labels = []
    clusters = [[] for _ in range(node_set.num)]
    root_index = [-1] * num
    temp = 0
    for i in range(num):
        if node_set.locate_root(i) == i:
            root_index[i] = temp
            labels.append(front_cluster[i])
            temp += 1
    for i in range(num):
        root = node_set.locate_root(i)
        clusters[root_index[root]].append(i)
        new_gt[int(i/size[1]), int(i%size[1]), :] = 255 if front_cluster[root] else 0  
    return I / U, new_img, new_gt, labels, clusters

# 外部接口
def apply(img, gt, res_path, max_cluster, min_cluester, min_size, k):
    img = np.array(img).astype(int)
    gt = np.array(gt)
    edges = init_edges(img, img.shape[0], img.shape[1])
    node_set = segment(edges, img.shape[0]*img.shape[1], max_cluster, min_cluester, min_size, k)
    IOU, new_img, new_gt, labels, clusters = compute(node_set, img, gt, img.shape)
    cv2.imwrite(res_path + "seg.png", new_img)
    cv2.imwrite(res_path + "gt.png", new_gt)
    return IOU, node_set.num, labels, clusters

if __name__ == "__main__":   
    sum, total = 0, 0
    for i in range(74, 1000, 100):
        res_path = "../result/2/" + str(i) + '/'
        if not os.path.exists(res_path):
            os.mkdir(res_path)
        png_name = str(i) + ".png"
        img_name = "../data/imgs/" + png_name
        gt_name = "../data/gt/" + png_name
        img = cv2.imread(img_name)
        gt = cv2.imread(gt_name)
        IOU, _, _, _ = apply(img, gt, res_path, 70, 50, 50, 117)
        sum += IOU
        total += 1
        print(png_name, IOU)
    print(sum / total)
