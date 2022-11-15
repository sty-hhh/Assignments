close all;clc;clear all;
I = imread('Fig0418(a).tif');
I = double(I);
a = 20;
[h,L] = gauss(I,a,1);
l1 = I - h;
[l2,L] = gauss(I,a,0);
figure,
subplot(221),imshow(uint8(I));
title('Fig.4.18(a)原图')
subplot(222),imshow(L);
title('高斯高通滤波器')
subplot(223),imshow(uint8(l1));
title({'Fig.4.18(a)钝化模板';'(原图减低通)'})
subplot(224),imshow(uint8(l2));
title({'Fig.4.26(a)钝化模板';'(高通)'})

function [g, L] = gauss(img,a,lowpass_flag)
	[M,N] = size(img);
    % 延拓
	P = 2 * M; 
    Q = 2 * N; 
    % 添加0
    fp = zeros(P,Q);
	fp(1:M,1:N) = img(1:M,1:N);
    % 频谱中心化处理
    [Y,X] = meshgrid(1:Q,1:P);
    ones = (-1).^(X+Y);
	fp = ones.*fp;
    % 傅里叶变换
    FLY = fft2(fp);
    % 高斯滤波
    H = zeros(P,Q);
    L = zeros(P,Q);
    for i=1:P
        for j=1:Q
            H(i,j) = exp((-(i-M)^2-(j-N)^2)/(2*a^2));
            L(i,j) = 1 - H(i,j);
        end
    end
    if lowpass_flag == 1
		G = H.*FLY;
	else
		G = L.*FLY;
    end
    % 傅里叶逆变换，恢复原图像
    g = real(ifft2(G));
    % 从左上角提取 M*N 大小区域
    g = ones.*g;
    g = g(1:M,1:N);
end