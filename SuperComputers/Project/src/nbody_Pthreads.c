#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <pthread.h>
#include <sys/time.h>

#define  DIM      3			// 维数
#define  X        0
#define  Y        1
#define  Z        2
#define  N        1024		// 粒子数
#define  G        1			// 引力常量
#define  dT       0.005		// 时间差	
#define  n_steps  20		// 迭代数
#define  BLOCK    0			// 块调度
#define  CYCLIC   1			// 循环调度

#define  GET_TIME(now) { \
    struct timeval t; \
    gettimeofday(&t, NULL); \
    now = t.tv_sec + t.tv_usec/1000000.0; \
}

double          start,stop;
double          masses[N];			// 质量
double          pos[N][DIM];		// 位置
double          vel[N][DIM];		// 速度
double          forces[N][DIM];		// 作用力
int             thread_count;		// 线程数
int             b_thread_count;     // 路障计数器
pthread_mutex_t b_mutex;            // 路障互斥量
pthread_cond_t  b_cond_var;         // 路障条件变量

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
    FILE *fp = fopen("nbody_Pthreads_out.txt", "w");
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

void Loop_schedule(int my_rank, int thread_count, int sched, int* first_p, int* last_p, int* incr_p) {
    if (sched == CYCLIC) {  	// 循环调度，每个线程从自己线程编号开始，每隔thread_count个元素取一个
        *first_p = my_rank;
        *last_p = N;
        *incr_p = thread_count;
    }
    else {                  	// 块调度，每个线程平均取N/thread_count个
        *incr_p = 1;
        *first_p = my_rank * N / thread_count;
        *last_p = *first_p + N / thread_count;
    }
}

void Barrier_init() {	// 初始化路障
    b_thread_count = 0;
    pthread_mutex_init(&b_mutex, NULL);
    pthread_cond_init(&b_cond_var, NULL);
}

void Barrier() {	// 用条件变量和互斥量实现路障
    pthread_mutex_lock(&b_mutex);
    b_thread_count++;
    if (b_thread_count == thread_count) {
        b_thread_count = 0;
        pthread_cond_broadcast(&b_cond_var);
    }
    else
        while (pthread_cond_wait(&b_cond_var, &b_mutex) != 0);
    pthread_mutex_unlock(&b_mutex);
}

void Barrier_destroy() {	// 销毁路障
    pthread_mutex_destroy(&b_mutex);
    pthread_cond_destroy(&b_cond_var);
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

void* Thread_compute(void* rank) {	// 线程操作
    long my_rank = (long)rank;
    int first, last, incr;	// 循环变量的初始值、最终值、增量
    int step, part;
    Loop_schedule(my_rank, thread_count, BLOCK, &first, &last, &incr);
    for (step = 1; step <= n_steps; step++) {	// 迭代20次
        memset(forces, 0, sizeof(forces));
        Barrier();	// 路障
        for (part = first; part < last; part += incr)
            Compute_force(part);
        Barrier();	// 路障
        for (part = first; part < last; part += incr)
            Compute_POSandVEL(part);
        Barrier();	// 路障
    }
    return NULL;
}

int main(int argc, char* argv[]) {
    long thread;
    pthread_t* thread_handles;
    if (argc == 2)
        thread_count = strtol(argv[1], NULL, 10);
    if (N % thread_count != 0) {
        fprintf(stderr, "thread_count %d can not divide N!\n", thread_count);
        exit(0);
    }
    thread_handles = (pthread_t*)malloc(thread_count * sizeof(pthread_t));
    Barrier_init();		// 初始化路障
    GET_TIME(start);
    init();
    for (thread = 0; thread < thread_count; thread++)
        pthread_create(&thread_handles[thread], NULL, Thread_compute, (void*)thread);	// 启动线程
    for (thread = 0; thread < thread_count; thread++)
        pthread_join(thread_handles[thread], NULL);		// 停止线程
    print();
    GET_TIME(stop);
    printf("Run time: %e\n", stop-start);
    Barrier_destroy();	// 销毁路障
    free(thread_handles);
    return 0;
}