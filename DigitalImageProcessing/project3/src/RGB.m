close all;clear all;clc;

I1 = imread('1.jpeg');
BW_rgb1 = rgb_face(I1);
bb_rgb1 = get_bb(BW_rgb1);
I2 = imread('2.jpeg');
BW_rgb2 = rgb_face(I2);
bb_rgb2 = get_bb(BW_rgb2);
I3 = imread('3.jpeg');
BW_rgb3 = rgb_face(I3);
bb_rgb3 = get_bb(BW_rgb3);

figure, subplot(1,2,2);
imshow(BW_rgb1)
title('分割图');
subplot(1,2,1);
imshow(I1);
rectangle('Position',bb_rgb1,'EdgeColor','r');
title('基于RGB的人脸检测');

figure, subplot(1,2,2);
imshow(BW_rgb2)
title('分割图');
subplot(1,2,1);
imshow(I2);
rectangle('Position',bb_rgb2,'EdgeColor','r');
title('基于RGB的人脸检测');

figure, subplot(1,2,2);
imshow(BW_rgb3)
title('分割图');
subplot(1,2,1);
imshow(I3);
rectangle('Position',bb_rgb3,'EdgeColor','r');
title('基于RGB的人脸检测');

function bw = rgb_face(I)
	[m,n,c] = size(I); % 获取图像
	BW = zeros(m,n);
	for i = 1:m
		for j = 1:n
			R = I(i,j,1);
			G = I(i,j,2);
			B = I(i,j,3);
			v = [R,G,B];
			if (R > 95 && G > 40 && B > 20) && ((max(v) - min(v) > 15 && abs(R-G) > 15 && R > G && R > B)) % 均匀照明（白天）
            % if R > 20 && G > 210 && B > 170 && abs(R-G) < 15 && R > G && % R > B) % 潜在照明（黑夜）
                BW(i,j) = 1;
            end
		end
	end
	bw = BW;
end

function g = get_bb(BW)
	L = bwlabel(BW,8); % 返回和BW相同大小的8连通矩阵
	BB = regionprops(L,'BoundingBox'); % 返回最小矩阵的结构体
	BB1 = struct2cell(BB); % 将结构体转换为元胞数组
	BB2 = cell2mat(BB1); % 元胞数组转为矩阵
    % 二值图所以连通只有1，大小1*4n，每4个[x,y,w,h]代表矩形的从点(x,y)开始绘制一个宽w高h的矩形。

	[s1,s2] = size(BB2);
	max_area = 0;
    j = 3;
	for k = 3:4:s2-1
	    area_bb = BB2(1,k) * BB2(1,k+1); % 计算值矩阵大小
	    if area_bb > max_area && (BB2(1,k) / BB2(1,k+1)) < 1.8
	        max_area = area_bb;
	        j = k;
	    end
    end
	g = [BB2(1,j-2),BB2(1,j-1),BB2(1,j),BB2(1,j+1)];
end