# README

nbody_init.txt是给定的标准输入文件

nbody_last.txt是给定的标准输出文件

nbody_serial_out.txt是串行版本的输出文件

nbody_OpenMP_out.txt是OpenMP版本的输出文件

nbody_Pthreads_out.txt是Pthreads版本的输出文件

nbody_serial_out.txt，nbody_OpenMP_out.txt和nbody_Pthreads_out.txt的结果完全一致，与nbody_last.txt在位置pos的三个值上有10^-8数量级的误差，在速度vel的三个值上有10 ^-6数量级的误差。