#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/time.h>

#define  DIM      3			// 维数
#define  X        0
#define  Y        1
#define  Z        2
#define  N        1024		// 粒子数
#define  G        1			// 引力常量
#define  dT       0.005		// 时间差			
#define  n_steps  20		// 迭代数

#define  GET_TIME(now) { \
    struct timeval t; \
    gettimeofday(&t, NULL); \
    now = t.tv_sec + t.tv_usec/1000000.0; \
}

double start,stop;
double masses[N];			// 质量
double pos[N][DIM];			// 位置
double vel[N][DIM];			// 速度
double forces[N][DIM];		// 作用力

void init() {	// 从文本文件中输入			
    FILE *fp = fopen("nbody_init.txt", "r");
    if (fp == NULL) {
        printf("File cannot open! ");
        exit(0);
    }
    for (int i = 0; i < N; i++) {
        fscanf(fp, "%lf", &masses[i]);
        fscanf(fp, "%lf", &pos[i][X]);
        fscanf(fp, "%lf", &pos[i][Y]);
        fscanf(fp, "%lf", &pos[i][Z]);
        fscanf(fp, "%lf", &vel[i][X]);
        fscanf(fp, "%lf", &vel[i][Y]);
        fscanf(fp, "%lf", &vel[i][Z]);
    }
    fclose(fp);
}

int digit(double x) {	// 用于判断一个数整数部分的位数
    int k = 0;
    int y = abs((int)x);
    while (y > 0) {
        y /= 10;
        ++k;
    }
    return k;
}

void print() {	// 输出到文本文件
    FILE *fp = fopen("nbody_serial_out.txt", "w");
    if (fp == NULL) {
        printf("File cannot open! ");
        exit(0);
    }
    for (int i = 0; i < N; i++) {
        fprintf(fp, "%.*lf ", 15-digit(masses[i]), masses[i]);		// 控制输出为15位有效数字
        fprintf(fp, "%.*lf ", 15-digit(pos[i][X]), pos[i][X]);
        fprintf(fp, "%.*lf ", 15-digit(pos[i][Y]), pos[i][Y]);
        fprintf(fp, "%.*lf ", 15-digit(pos[i][Z]), pos[i][Z]);
        fprintf(fp, "%.*lf ", 15-digit(vel[i][X]), vel[i][X]);
        fprintf(fp, "%.*lf ", 15-digit(vel[i][Y]), vel[i][Y]);
        fprintf(fp, "%.*lf ", 15-digit(vel[i][Z]), vel[i][Z]);
        fprintf(fp, "\n");
    }
    fclose(fp);
}

void Compute_force(int q) {		// 计算作用力
    double x_diff, y_diff, z_diff, dist, dist_cubed;
    for (int k = 0; k < N; k++) {
        if (k == q) continue;
        x_diff = pos[q][X] - pos[k][X];
        y_diff = pos[q][Y] - pos[k][Y];
        z_diff = pos[q][Z] - pos[k][Z];
        dist = sqrt(x_diff*x_diff + y_diff*y_diff + z_diff*z_diff);
        dist_cubed = dist*dist*dist;
        forces[q][X] -= G*masses[q]*masses[k]/dist_cubed * x_diff;
        forces[q][Y] -= G*masses[q]*masses[k]/dist_cubed * y_diff;
        forces[q][Z] -= G*masses[q]*masses[k]/dist_cubed * z_diff;
    }
}

void Compute_POSandVEL(int q) {		// 计算速度和位置
    vel[q][X] += dT/masses[q]*forces[q][X];
    vel[q][Y] += dT/masses[q]*forces[q][Y];
    vel[q][Z] += dT/masses[q]*forces[q][Z];
    pos[q][X] += dT*vel[q][X];
    pos[q][Y] += dT*vel[q][Y];
    pos[q][Z] += dT*vel[q][Z];  
}

int main(int argc, char* argv[]) {
    GET_TIME(start);
    init();
    for (int step = 1; step <= n_steps; step++) {	// 迭代20次
        memset(forces, 0, sizeof(forces));
        for (int part = 0; part < N; part++) 
            Compute_force(part);
        for (int part = 0; part < N; part++) 
            Compute_POSandVEL(part);
    }
    print();
    GET_TIME(stop);
    printf("Run time: %e\n", stop-start);
}