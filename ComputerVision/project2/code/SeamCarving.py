import cv2
import math
import os
import imageio
import numpy as np

class seamCarving():
    # 初始化
    def __init__(self, img, gt, ratio):
        self.img = img.astype(np.float64)
        self.height = math.ceil(self.img.shape[0] * ratio)
        self.width = math.ceil(self.img.shape[1] * ratio)
        self.out_img = np.copy(self.img)
        B, G, R = cv2.split(gt) 
        self.mask = (B != 0) & (G != 0) & (R != 0)

    # 计算能量
    def cal_energy(self):
        B, G, R = cv2.split(self.out_img)
        b = np.abs(cv2.Scharr(B, -1,1,0)) + np.abs(cv2.Scharr(B, -1,0,1))
        g = np.abs(cv2.Scharr(G, -1,1,0)) + np.abs(cv2.Scharr(G, -1,0,1))
        r = np.abs(cv2.Scharr(R, -1,1,0)) + np.abs(cv2.Scharr(R, -1,0,1))
        return r + g + b

    # 寻找seam
    def locate(self):
        energy = self.cal_energy().astype(int)
        mask = np.copy(self.mask).astype(int)
        mask[mask > 0] = 1e9
        energy = energy + mask
        temp = np.zeros(energy.shape)
        temp[0] = energy[0]
        pre = np.zeros(energy.shape, dtype=int)
        m, n = energy.shape
        for i in range(1, m):
            for j in range(n):
                if j == 0:
                    p = temp[i-1][j] + np.abs(self.out_img[i][j+1]).sum()
                    q = temp[i-1][j+1] + np.abs(self.out_img[i-1][j] - self.out_img[i][j+1]).sum() + np.abs(self.out_img[i][j+1]).sum()
                    min_val = p if p < q else q
                    pre[i][j] = 0 if p < q else 1
                elif j == n - 1:
                    p = temp[i-1][j-1] + np.abs(self.out_img[i-1][j] - self.out_img[i][j-1]).sum() + np.abs(self.out_img[i][j-1]).sum()
                    q = temp[i-1][j] + np.abs(self.out_img[i][j-1]).sum()
                    min_val = p if p < q else q
                    pre[i][j] = -1 if p < q else 0
                else:
                    p = temp[i-1][j-1] + np.abs(self.out_img[i][j+1] - self.out_img[i][j-1]).sum() + np.abs(self.out_img[i-1][j] - self.out_img[i][j-1]).sum()
                    q = temp[i-1][j] + np.abs(self.out_img[i][j+1] - self.out_img[i][j-1]).sum()
                    t = temp[i-1][j+1] + np.abs(self.out_img[i][j+1] - self.out_img[i][j-1]).sum() + np.abs(self.out_img[i-1][j] - self.out_img[i][j+1]).sum()
                    min_val = np.min([p, q, t])
                    pre[i][j] = np.argmin([p, q, t]) - 1
                temp[i][j] = min_val + energy[i][j]
        path = np.zeros(m, dtype = int)
        path[m - 1] = temp[m - 1].argmin()
        for i in list(reversed(list(range(m - 1)))):
            path[i] = path[i + 1] + pre[i][path[i + 1]]
        return path

    # 保存seam
    def save(self, path, rotate, dir, name): 
        self.out_img[range(self.out_img.shape[0]), path] = np.array([0,0,255])
        if not os.path.exists(dir):
            os.makedirs(dir)
        pic_name = dir + "/" + name
        print(pic_name)
        if rotate:
            out_img = np.rot90(self.out_img, 3)
        else:
            out_img = self.out_img
        cv2.imwrite(pic_name, out_img)
    
    # 删除seam
    def delete(self, path):
        temp_image = np.zeros((self.out_img.shape[0], self.out_img.shape[1] -1, 3)).astype(np.uint8)
        temp_mask = np.zeros((self.mask.shape[0], self.mask.shape[1]-1)).astype(bool)
        for i in range(len(path)):
            temp_image[i][:path[i]] = self.out_img[i][:path[i]]
            temp_image[i][path[i]:] = self.out_img[i][path[i] + 1:]
            temp_mask[i][:path[i]] = self.mask[i][:path[i]]
            temp_mask[i][path[i]:] = self.mask[i][path[i] + 1:]
        self.out_img  = temp_image.astype(np.uint8)
        self.mask = temp_mask
    
    # 外部接口
    def apply(self, dir):
        for i in range(self.img.shape[1] - self.width):
            path = self.locate()
            self.save(path, False, dir, str(i) + '.png')
            self.delete(path)
        self.out_img = np.rot90(self.out_img)
        self.mask = np.rot90(self.mask)
        for i in range(self.img.shape[0] - self.height):
            path = self.locate()
            self.save(path, True, dir, str(i + self.img.shape[1] - self.width) + '.png')
            self.delete(path)
        self.out_img = np.rot90(self.out_img, 3)
        return self.out_img

# 转为gif
def img2gif(path, gif_name):
    img_list = os.listdir(path)
    img_list.sort(key=lambda x : int(x[:-4]))
    frames = []
    for img in img_list:
        name = path + '/' + img
        frames.append(imageio.imread(name))
    imageio.mimsave(gif_name, frames, 'GIF', fps=5)


work_path = "../result/1/temp/"
res_path = "../result/1/"
if not os.path.exists(work_path):
    os.makedirs(work_path)
for i in range(74, 1000, 100):
    png_name = str(i) + ".png"
    img_name = "../data/imgs/" + png_name
    gt_name = "../data/gt/" + png_name
    img = cv2.imread(img_name)
    gt = cv2.imread(gt_name)
    back = (gt == 0).sum()                       # 背景大小
    size = (gt == 0).sum() + (gt != 0).sum()     # 原图面积
    ratio = math.sqrt(1 - back / (size * 2))     # x轴和y轴缩放比例

    func = seamCarving(img, gt, ratio)
    total_num = func.img.shape[0] + func.img.shape[1] - func.height - func.width + 1
        
    out_img = func.apply(work_path + str(i))
    cv2.imwrite(res_path + png_name, out_img)
    cv2.imwrite(work_path + str(i) + "/" + "0.png", func.img)
    cv2.imwrite(work_path + str(i) + "/" + str(total_num) + ".png", out_img)
    img2gif(work_path + str(i), res_path + str(i) + ".gif")

