close all;clc;

I = imread('Fig0340(a)(dipxe_text).tif');  % 读入图像
I = im2double(I);       % 原图像
L = zeros(size(I));          % 零矩阵，等会用来存放拉普拉斯变换后的图像
[M,N] = size(I);             % 原图像的大小

% 以下计算拉普拉斯变换后的图像
for i = 2:M-1
	for j = 2:N-1
        L(i,j) = -I(i-1,j-1)-I(i-1,j)-I(i-1,j+1)-I(i,j-1)+8*I(i,j)-I(i,j+1)-I(i+1,j-1)-I(i+1,j)-I(i+1,j+1);
	end
end

% 以下分别画出 I，L，I+L
subplot(1,3,1); imshow(im2uint8(I)); title('原图像')
subplot(1,3,2); imshow(im2uint8(L)); title('Laplacian变换后的图像')
subplot(1,3,3); imshow(im2uint8(I+L)); title('锐化结果')