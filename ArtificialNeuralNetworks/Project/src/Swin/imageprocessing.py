import os
import cv2
from tqdm import tqdm

inpath = "./Skin40"
outpath = './skin40Out'

try:
    os.mkdir(outpath)
except:
    pass
count = 0

for filefold in tqdm(os.listdir(inpath)):
    fold = inpath + '/' + filefold
    try:
        os.mkdir(outpath + '/' + filefold)

    except:
        
        pass
    count += 1
    for jpg in os.listdir(fold):
        img = cv2.imread(fold + "/" + jpg,cv2.IMREAD_COLOR)
        shape = img.shape
        copter = img[0:shape[0]-70,0:shape[1],:]
        shape = copter.shape
        # if shape[0] < shape[1]:
        #     shorter = shape[0]
        #     mid = (shape[1]-shorter)/2
        #     mid = int(mid)
        #     copter = copter[:,mid:mid+shorter,:]
        # else:
        #     mid = (shape[0]-shape[1])/2
        #     mid = int(mid)
        #     copter = copter[mid:mid+shape[1],:,:]
        # copter = cv2.resize(copter,(224,224))
        randomName = jpg
        cv2.imwrite(outpath + '/' + filefold + '/' + randomName, copter)
