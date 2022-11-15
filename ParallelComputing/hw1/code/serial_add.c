#include <stdio.h>
#include <sys/time.h>

/* 获取时间 */
#define  GET_TIME(now) { \
    struct timeval t; \
    gettimeofday(&t, NULL); \
    now = t.tv_sec + t.tv_usec/1000000.0; \
}

int N = 1000000;    /* 设有 N = 1000000 个数相加 */
int i, result;
double start, stop;

int main(int argc, char* argv[]) {
    int s[N];
    for (i = 0; i < N; ++i)     /* 将N个数设为1 */
        s[i] = 1;
    GET_TIME(start);
    for (i = 0; i < N; ++i)     /* 串行求和 */
        result += s[i];
    GET_TIME(stop);
    printf("%d\n", result);     /* 输出结果 */
    printf("Run time: %e\n", stop-start);   /* 计算时间 */
}