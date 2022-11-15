clear;
clc;
I = imread('figure32.jpg');
Ihist = zeros(1,256);
[m,n] = size(I);
for i = 1:256
    Ihist(i) = sum(sum(I==i-1));
end
probability_sum = zeros(1,256);
for i = 1:256
    for j = 1:i
        probability_sum(i) = probability_sum(i) + 255*Ihist(j)/(m*n);
    end
end
newI = zeros(m,n);
for i = 1:m
    for j = 1:n
        newI(i,j) = uint8(probability_sum(I(i,j)+1));
    end
end

newIhist = zeros(1,256);
for i = 1:256
    newIhist(i) = sum(sum(newI==i-1));
end
figure,
subplot(121),imshow(uint8(I));
title('原始图像')
subplot(122),imshow(uint8(newI));
title('均衡化图像')
figure,
subplot(121),bar(0:255,uint32(Ihist));
title('原始图像直方图');
subplot(122),bar(0:255,uint32(newIhist));
title('均衡化图像直方图');
