#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <ctime>
#include <cmath>
#include <cstring>
#include <omp.h>
#include "utils.h"
using namespace std;

int main(int argc, char *argv[]) {
    int *in;
    float *out;
    // 随机初始化矩阵
    int m = strtol(argv[1], NULL, 10);
    int n = strtol(argv[2], NULL, 10);
    Generate(&in, &out, m, n);
    // 线程数
    int thread_num = strtol(argv[3], NULL, 10);
    // 预处理
    float pre_cal[26] = {0.0, 1.0 * log2f(1.0), 2.0 * log2f(2.0), 3.0 * log2f(3.0), 4.0 * log2f(4.0), 5.0 * log2f(5.0),
                        6.0 * log2f(6.0), 7.0 * log2f(7.0), 8.0 * log2f(8.0), 9.0 * log2f(9.0), 10.0 * log2f(10.0),
                        11.0 * log2f(11.0), 12.0 * log2f(12.0), 13.0 * log2f(13.0), 14.0 * log2f(14.0), 15.0 * log2f(15.0),
                        16.0 * log2f(16.0), 17.0 * log2f(17.0), 18.0 * log2f(18.0), 19.0 * log2f(19.0), 20.0 * log2f(20.0),
                        21.0 * log2f(21.0), 22.0 * log2f(22.0), 23.0 * log2f(23.0), 24.0 * log2f(24.0), 25.0 * log2f(25.0)};
    // 开始时间
    double start = omp_get_wtime();
    // OpenMP计算
    int cnt[16];
#   pragma omp parallel for num_threads(thread_num) private(cnt)
        for (int i = 0; i < m; ++i)
            for (int j = 0; j < n; ++j) {
                int count = 0;
                memset(cnt, 0, sizeof(cnt));
                for (int dx = -2; dx <= 2; ++dx) {
                    const int x = i + dx;
                    if (x >= 0 && x < m) {
                        for (int dy = -2; dy <= 2; ++dy) {
                            const int y = j + dy;
                            if (y >= 0 && y < n) {
                                ++cnt[in[x*n+y]];
                                ++count;
                            }
                        }
                    }
                }
                double ans = 0;
                for (int k = 0; k < 16; ++k)
                    if (cnt[k])
                        ans -= (double)cnt[k] *  (1.0 / count) * (pre_log[cnt[k]]-pre_log[count]);
                out[i*n+j] = ans;
            }
    // 输出运行时间
    double end = omp_get_wtime();
    printf("Time cost (OpenMP): %.3f ms\n", (end - start) * 1000);
    // 检验正确性
    Evaluate(in, out, m, n);
    return 0;
}
