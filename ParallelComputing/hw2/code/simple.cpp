#include<bits/stdc++.h>
using namespace std;

#define N 256

void multiply(int **A, int **B, int **C) {
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            for (int k = 0; k < N; ++k)
                C[i][j] += A[i][k] * B[k][j];
}

int main() {
    int **A = new int*[N];
    int **B = new int*[N];
    int **C = new int*[N];
    for(int i = 0; i < N; ++i) {
        A[i] = new int[N];
        B[i] = new int[N];
        C[i] = new int[N];
        memset(A[i], 0, sizeof(int)*N);
        memset(B[i], 0, sizeof(int)*N);
        memset(C[i], 0, sizeof(int)*N);
    }
    multiply(A, B, C);
    return 0;
}