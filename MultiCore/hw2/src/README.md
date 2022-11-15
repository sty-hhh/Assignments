# README

- utils.h：包括CUDA调用的检查宏CHECK，随机初始化矩阵等通用函数
- kernel.cu：CUDA调用的各种优化版本的核函数
- main_cuda.cu：CUDA主函数
- main_omp.cpp：OpenMP主函数及实现

上面4个文件可用命令行设置任意大小的矩阵进行性能测试，运行方法详见report

- main.cu是将代码移植到给定文件后的版本
- output1.bin和output2.bin是输出的$8 \times 8$和$2048 \times 2048$矩阵