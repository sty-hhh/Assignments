#%%
import math
from PIL import Image
import numpy as np
import networkx as nx
import copy

STAT_OBSTACLE='#'
STAT_NORMAL='.'

class RoadMap():
    def __init__(self,img_file):
        # 图片变二维数组
        test_map = []
        img = Image.open(img_file)
        img_gray = img.convert('L')  # 地图灰度化
        img_arr = np.array(img_gray)
        img_binary = np.where(img_arr<127,0,255)
        for x in range(img_binary.shape[0]):
            temp_row = []
            for y in range(img_binary.shape[1]):
                status = STAT_OBSTACLE if img_binary[x,y]==0 else STAT_NORMAL 
                temp_row.append(status)
            test_map.append(temp_row)
            
        self.map = test_map
        self.cols = len(self.map[0])
        self.rows = len(self.map)
        
    def is_valid_xy(self, x,y):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            return False
        return True

    def not_obstacle(self,x,y):
        return self.map[x][y] != STAT_OBSTACLE
    
    def EuclidenDistance(self, xy1, xy2):
        dis = 0
        for (x1, x2) in zip(xy1, xy2):
            dis += (x1 - x2)**2
        return dis**0.5

    def check_path(self, xy1, xy2):
        steps = max(abs(xy1[0]-xy2[0]), abs(xy1[1]-xy2[1])) # 取横向、纵向较大值，确保经过的每个像素都被检测到
        xs = np.linspace(xy1[0],xy2[0],steps+1)
        ys = np.linspace(xy1[1],xy2[1],steps+1)
        for i in range(1, steps): # 第一个节点和最后一个节点是 xy1，xy2，无需检查
            if not self.not_obstacle(math.ceil(xs[i]), math.ceil(ys[i])):
                return False
        return True

    def plot(self,path):
        out = []
        for x in range(self.rows):
            temp = []
            for y in range(self.cols):
                if self.map[x][y]==STAT_OBSTACLE:
                    temp.append(0)
                elif self.map[x][y]==STAT_NORMAL:
                    temp.append(255)
                else:
                    temp.append(255)
            out.append(temp)
        for x,y in path:
            out[x][y] = 127
        out = np.array(out,dtype=np.uint8)
        img = Image.fromarray(out)
        img.show()

    def plot_nodes(self,nodes):
        out = []
        for x in range(self.rows):
            temp = []
            for y in range(self.cols):
                if self.map[x][y]==STAT_OBSTACLE:
                    temp.append(0)
                elif self.map[x][y] in nodes:
                    temp.append(0)
                else:
                    temp.append(255)
            out.append(temp)
        
        out = np.array(out,dtype=np.uint8)
        img = Image.fromarray(out)
        img.show()
    
    def plot_edges(self,edges):
        out = []
        for x in range(self.rows):
            temp = []
            for y in range(self.cols):
                if self.map[x][y]==STAT_OBSTACLE:
                    temp.append(0)
                else:
                    temp.append(255)
            out.append(temp)
        for x,y in edges:
            out[x][y] = 127
        out = np.array(out,dtype=np.uint8)
        img = Image.fromarray(out)
        img.show()

class PRM(RoadMap):
    def __init__(self, img_file, **param):
        RoadMap.__init__(self,img_file)
        self.num_sample = param['num_sample'] 
        self.distance_neighbor = param['distance_neighbor'] 
        self.G = nx.Graph() 
        
    def learn(self):
        # 随机采样节点
        while len(self.G.nodes)<self.num_sample:
            XY = (np.random.randint(0, self.rows),np.random.randint(0, self.cols)) # 随机取点
            if self.is_valid_xy(XY[0],XY[1]) and self.not_obstacle(XY[0],XY[1]): # 不是障碍物点
                self.G.add_node(XY)
        self.plot(self.G.nodes)
        # 邻域范围内进行碰撞检测，加边
        for node1 in self.G.nodes:
            for node2 in self.G.nodes:
                if node1==node2:
                    continue
                dis = self.EuclidenDistance(node1,node2)
                if dis<self.distance_neighbor and self.check_path(node1,node2):
                    self.G.add_edge(node1,node2,weight=dis)
    
    def find_path(self,startXY=None,endXY=None):
        # 寻路时再将起点和终点添加进图中
        temp_G = copy.deepcopy(self.G)
        startXY = tuple(startXY) 
        endXY = tuple(endXY) 
        temp_G.add_node(startXY)
        temp_G.add_node(endXY)
        for node1 in [startXY, endXY]: # 将起点和目的地连接到图中
            for node2 in temp_G.nodes:
                dis = self.EuclidenDistance(node1,node2)
                if dis<self.distance_neighbor and self.check_path(node1,node2):
                    temp_G.add_edge(node1,node2,weight=dis) # 边的权重为 欧几里得距离
        edges = self.construct_all_path(temp_G.edges)
        self.plot_edges(edges)
        # 直接调用networkx中求最短路径的方法
        path = nx.shortest_path(temp_G, source=startXY, target=endXY)
        return self.construct_path(path)

    def construct_path(self, path):
        # find_path寻路得到的是连通图的节点，扩展为经过的所有像素点
        out = []
        for i in range(len(path)-1):
            xy1,xy2=path[i],path[i+1]
            steps = max(abs(xy1[0]-xy2[0]), abs(xy1[1]-xy2[1])) # 取横向、纵向较大值，确保经过的每个像素都被检测到
            xs = np.linspace(xy1[0],xy2[0],steps+1)
            ys = np.linspace(xy1[1],xy2[1],steps+1)
            for j in range(0, steps+1): 
                out.append((math.ceil(xs[j]), math.ceil(ys[j])))
        return out

    def construct_all_path(self, path):
        out = []
        for p in path:
            xy1,xy2=p[0],p[1]
            steps = max(abs(xy1[0]-xy2[0]), abs(xy1[1]-xy2[1])) # 取横向、纵向较大值，确保经过的每个像素都被检测到
            xs = np.linspace(xy1[0],xy2[0],steps+1)
            ys = np.linspace(xy1[1],xy2[1],steps+1)
            for j in range(0, steps+1): 
                out.append((math.ceil(xs[j]), math.ceil(ys[j])))
        return out

prm = PRM('maze.png',num_sample=1000,distance_neighbor=200)
prm.learn()
path = prm.find_path((50,528),(730,30))
prm.plot(path)

# %%
