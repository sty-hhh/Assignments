#include <stdio.h>
#include <immintrin.h>
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
__m256i n;

int main(int argc, char* argv[]) {
    __m256i s[N/8 + 1];
    for(int i = 0; i < N/8; ++i)    /* 将N个数设为1 */
        s[i] = _mm256_set1_epi32(1);
    GET_TIME(start);
    n = _mm256_load_si256((const __m256i *)(s));
    for (int i = 1; i < N/8; ++i)   /* 256位一组求和 */
        n = _mm256_add_epi32(n, s[i]);
    int sum[20];
    _mm256_store_ps((float *)sum, (__m256)n);
    for (i = 0; i < 8; ++i)         /* 8个数求和 */
        result += sum[i];
    GET_TIME(stop);
    printf("%d\n", result);     /* 输出结果 */
    printf("Run time: %e\n", stop-start);   /* 计算时间 */
}