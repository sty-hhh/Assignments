#include<bits/stdc++.h>
using namespace std;

#define N 256
int n = N;

void help(int *s, int *one, int *two, int *three, int *four) {
    int left = s[0];
    int right = s[1];
    int top = s[2];
    int bottom = s[3];

    one[0] = left;
    one[1] = (left + right) / 2;
    one[2] = top;
    one[3] = (top + bottom) / 2;
    
    two[0] = (left + right + 1) / 2;
    two[1] = right;
    two[2] = top;
    two[3] = (top + bottom) / 2;
    
    three[0] = left;
    three[1] = (left + right) / 2;
    three[2] = (top + bottom + 1) / 2;
    three[3] = bottom;
    
    four[0] = (left + right + 1) / 2;
    four[1] = right;
    four[2] = (top + bottom + 1) / 2;
    four[3] = bottom;
}

void divide(int **A, int **B, int **C, int *A_size,int *B_size) {
    if (n == 2) {
        C[A_size[2]][B_size[0]] = A[A_size[2]][A_size[0]]*B[B_size[2]][B_size[0]]+A[A_size[2]][A_size[1]]*B[B_size[3]][B_size[0]]+C[A_size[2]][B_size[0]];
        C[A_size[2]][B_size[1]] = A[A_size[2]][A_size[0]]*B[B_size[2]][B_size[1]]+A[A_size[2]][A_size[1]]*B[B_size[3]][B_size[1]]+C[A_size[2]][B_size[1]];
        C[A_size[3]][B_size[0]] = A[A_size[3]][A_size[0]]*B[B_size[2]][B_size[0]]+A[A_size[3]][A_size[1]]*B[B_size[3]][B_size[0]]+C[A_size[3]][B_size[0]];
        C[A_size[3]][B_size[1]] = A[A_size[3]][A_size[0]]*B[B_size[2]][B_size[1]]+A[A_size[3]][A_size[1]]*B[B_size[3]][B_size[1]]+C[A_size[3]][B_size[1]];
    }
    else {
        n /= 2;
        int A_one[4], A_two[4], A_three[4], A_four[4];
        int B_one[4], B_two[4], B_three[4], B_four[4];

        help(A_size, A_one, A_two, A_three, A_four);
        help(B_size, B_one, B_two, B_three, B_four);

        divide(A, B, C, A_one, B_one);
        divide(A, B, C, A_two, B_three);
        divide(A, B, C, A_one, B_two);
        divide(A, B, C, A_two, B_four);
        divide(A, B, C, A_three, B_one);
        divide(A, B, C, A_four, B_three);
        divide(A, B, C, A_three, B_two);
        divide(A, B, C, A_four, B_four);
    }
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
    int a_shape[4] = {0, N-1, 0, N-1};
    int b_shape[4] = {0, N-1, 0, N-1};
    divide(A, B, C, a_shape, b_shape);
    return 0;
}
