close all;clear all;clc;
I=imread('pic0343.tif');
[m,n]=size(I);
I2=zeros(m,n);
I2=zeros(m,n);
for i = 2:m-1
	for j = 2:n-1
		avg = 1/9*(I(i+1,j)+I(i-1,j)+I(i,j+1)+I(i,j-1)+I(i,j)+I(i+1,j+1)+I(i+1,j-1)+I(i-1,j+1)+I(i-1,j-1));
		I2(i,j)=2*I(i,j)-uint8(avg);
        I3(i,j)=3*I(i,j)-uint8(avg);
	end
end
figure,
subplot(131),imshow(uint8(I));
title('原图');
subplot(132),imshow(uint8(I2));
title('高提升滤波(A=2)')
subplot(133),imshow(uint8(I3));
title('高提升滤波(A=3)');