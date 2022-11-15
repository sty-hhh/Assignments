#include<bits/stdc++.h>
using namespace std;

#define N 256
int n = N;

void ADD(int **A, int **B, int **C, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] =  A[i][j] + B[i][j];
}
void SUB(int **A, int **B, int **C, int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            C[i][j] =  A[i][j] - B[i][j];
}
void MUL( int **A, int **B, int **C, int n) {
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            for (int k = 0; k < n; ++k)
                C[i][j] += A[i][k] * B[k][j];
}

void strassen(int **A, int **B, int **C, int n) {
    int half = n / 2;
    if (n <= 16) {
        MUL(A, B, C, n);
        return;
    }
    int **A11 = new int*[half];int **A12 = new int*[half];
    int **A21 = new int*[half];int **A22 = new int*[half];
    int **B11 = new int*[half];int **B12 = new int*[half];
    int **B21 = new int*[half];int **B22 = new int*[half]; 
    int **C11 = new int*[half];int **C12 = new int*[half];
    int **C21 = new int*[half];int **C22 = new int*[half];

    int **S1 = new int*[half];int **S2 = new int*[half];
    int **S3 = new int*[half];int **S4 = new int*[half];
    int **S5 = new int*[half];int **S6 = new int*[half];
    int **S7 = new int*[half];int **S8 = new int*[half];
    int **S9 = new int*[half];int **S10 = new int*[half];

    int **P1 = new int*[half];int **P2 = new int*[half];
    int **P3 = new int*[half];int **P4 = new int*[half];
    int **P5 = new int*[half];int **P6 = new int*[half];
    int **P7 = new int*[half];

    for (int i = 0; i < half; i++) {
        A11[i] = new int[half];A12[i] = new int[half];
        A21[i] = new int[half];A22[i] = new int[half];
        B11[i] = new int[half];B12[i] = new int[half];
        B21[i] = new int[half];B22[i] = new int[half];
        C11[i] = new int[half];C12[i] = new int[half];
        C21[i] = new int[half];C22[i] = new int[half];

        S1[i] = new int[half];S2[i] = new int[half];
        S3[i] = new int[half];S4[i] = new int[half];
        S5[i] = new int[half];S6[i] = new int[half];
        S7[i] = new int[half];S8[i] = new int[half];
        S9[i] = new int[half];S10[i] = new int[half];

        P1[i] = new int[half];P2[i] = new int[half];
        P3[i] = new int[half];P4[i] = new int[half];
        P5[i] = new int[half];P6[i] = new int[half];
        P7[i] = new int[half];
    }
    for (int i = 0; i < half; ++i) {
        for (int j = 0; j < half; ++j) {
            A11[i][j] = A[i][j];
            A12[i][j] = A[i][j+half];
            A21[i][j] = A[i+half][j];
            A22[i][j] = A[i+half][j+half];
            B11[i][j] = B[i][j];
            B12[i][j] = B[i][j+half];
            B21[i][j] = B[i+half][j];
            B22[i][j] = B[i+half][j+half];
        }
    }
    SUB(B12, B22, S1, half);
    ADD(A11, A12, S2, half);
    ADD(A21, A22, S3, half);
    SUB(B21, B11, S4, half);
    ADD(A11, A22, S5, half);
    ADD(B11, B22, S6, half);
    SUB(A12, A22, S7, half);
    ADD(B21, B22, S8, half);
    SUB(A11, A21, S9, half);
    ADD(B11, B12, S10, half);

    strassen(A11, S1, P1, half);
    strassen(S2, B22, P2, half);
    strassen(S3, B11, P3, half);
    strassen(A22, S4, P4, half);
    strassen(S5, S6, P5, half);
    strassen(S7, S8, P6, half);
    strassen(S9, S10, P7, half);

    ADD(P4, P5, C11, half);SUB(C11, P2, C11, half);ADD(C11, P6, C11, half);
    ADD(P1, P2, C12, half);
    ADD(P3, P4, C21, half);
    ADD(P1, P5, C22, half);SUB(C22, P3, C22, half);SUB(C22, P7, C22, half);

    for (int i = 0; i < half; ++i) {
        for (int j = 0; j < half; ++j) {
            C[i][j] = C11[i][j];
            C[i][j+half] = C12[i][j];
            C[i+half][j] = C21[i][j];
            C[i+half][j+half] = C22[i][j];
        }
    }
    for (int i = 0; i < half; ++i) {
        delete[] A11[i];delete[] A12[i];delete[] A21[i];delete[] A22[i];
        delete[] B11[i];delete[] B12[i];delete[] B21[i];delete[] B22[i];
        delete[] C11[i];delete[] C12[i];delete[] C21[i];delete[] C22[i];
        delete[] S1[i];delete[] S2[i];delete[] S3[i];delete[] S4[i];delete[] S5[i];
        delete[] S6[i];delete[] S7[i];delete[] S8[i];delete[] S9[i];delete[] S10[i];
        delete[] P1[i];delete[] P2[i];delete[] P3[i];delete[] P4[i];
        delete[] P5[i];delete[] P6[i];delete[] P7[i];
    }
    delete[] A11;delete[] A12;delete[] A21;delete[] A22;
    delete[] B11;delete[] B12;delete[] B21;delete[] B22;
    delete[] C11;delete[] C12;delete[] C21;delete[] C22;
    delete[] S1;delete[] S2;delete[] S3;delete[] S4;delete[] S5;
    delete[] S6;delete[] S7;delete[] S8;delete[] S9;delete[] S10;
    delete[] P1;delete[] P2;delete[] P3;delete[] P4;
    delete[] P5;delete[] P6;delete[] P7;
}

int main(){
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
    strassen(A, B, C, n);
    return 0;
}
