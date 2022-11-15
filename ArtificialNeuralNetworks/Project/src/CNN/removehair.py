import os
import cv2
outpath = os.path.dirname(__file__) + '\\Skin40-copy\\'

def get_dataset(path):
    files = os.listdir(path)
    images = {}
    label = []
    index = 0
    for category in files:
        label.append(index)
        images[index] = []
        cur_file = path + category
        out_file = outpath + category
        image_paths = os.listdir(cur_file)
        for image_path in image_paths:
            image_file = cur_file + '\\' + image_path
            out_image_file = out_file + '\\' + image_path
            img = cv2.imread(image_file,1)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10)) # 矩形结构
            closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
            cv2.imwrite(out_image_file,closing)
            print(out_image_file)
    return images, label



def main():
    path = os.path.dirname(__file__) + '\\Skin40\\'
    images, label = get_dataset(path)


if __name__ == '__main__':
    main()