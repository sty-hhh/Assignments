close all;clc;clear all;
I1 = imread('Fig0441(a).jpg');
I2 = imread('Fig0441(b).jpg');
[m1,n1] = size(I1);
[m2,n2] = size(I2);
P = 298;
Q = 298;
img1 = zeros(P,Q);
img2 = zeros(P,Q);
img1(1:m1,1:n1) = I1(1:m1,1:n1);
img2(1:m2,1:n2) = I2(1:m2,1:n2);
% 生成网格采样点，用(-1)^(x+y)乘以原图像
[x,y]=meshgrid(1:P,1:Q);
ones=(-1).^(x+y);
% 傅里叶变换
f1 = fft2(ones.*img1);
f2 = fft2(ones.*img2);
% 求共轭
rel = f2 .* conj(f1);
% 傅里叶逆变换
newI = ifft2(rel);
newI = ones.*newI;
% 画图
figure,
subplot(131),imshow(I1);
title('Fig.4.41(a)原图')
subplot(132),imshow(I2);
title('Fig.4.41(b)原图')
subplot(133),imshow(mat2gray(newI));
title('Fig.4.41图像相关')
% 二维相关函数中最大值位置的(x,y)坐标
max_value = max(max(newI));
[row,col] = find(newI == max_value);
disp(['max value is : ', num2str(max_value)]);
disp(['row: ', num2str(row), ' col: ', num2str(col)])