#include <iostream>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <vector>
#include <omp.h>
#define BUFLEN 100
using namespace std;

typedef struct Element{
    int row, col;
    double val;
}Element;

void compute(int row, int col, vector<vector<Element>>& A, vector<vector<Element>>& B, 
            vector<vector<double>>& C, int thread_num) {
#   pragma omp parallel for num_threads(thread_num)
    for (int k = 1; k <= col; ++k)
        for (int i = 0; i < (int)A[k].size(); ++i)
            for (int j = 0; j < (int)B[k].size(); ++j) {
#               pragma omp atomic
                C[A[k][i].row][B[k][j].col] += A[k][i].val * B[k][j].val;
            }
}

int main(int argc, char *argv[]) {
    char buf[BUFLEN];
    int n, m, total, t;
    int thread_num = atoi(argv[1]);
    char* filename = argv[2];
    FILE* fp = fopen(filename,"r");
    fgets(buf, BUFLEN, fp);
    fgets(buf, BUFLEN, fp);
    fgets(buf, BUFLEN, fp);
    sscanf(buf, "%*s%d%d%d", &n, &m, &total);
    fgets(buf, BUFLEN, fp);
    fgets(buf, BUFLEN, fp);
    
    vector<int> rid;
    vector<int> cid;
    for (int i = 0; i < n; ++i) {
        fscanf(fp, "%d", &t);
        rid.push_back(t);
    }
    fscanf(fp, "%*d");
    for (int i = 0; i < total; ++i) {
        fscanf(fp, "%d", &t);
        cid.push_back(t);
    }

    vector<vector<Element>> A(m+1);
    vector<vector<Element>> B(n+1);
    vector<vector<double>> C(n+1);
    for (int i = 1; i <= n; ++i) 
        C[i].resize(m+1);
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= m; ++j)
            C[i][j] = 0.0;

    int col, row = 0;
    int rowptr = 1;
    for (int i = 0; i < 12; ++i) {
        char temp[30];
        double value;
        col = cid[i];
        fscanf(fp, "%s", temp);
        value = atof(temp);
        if (i >= rowptr-1) {
            row++;
            rowptr = rid[row];
        }
        Element e1 = {row, col, value};
        Element e2 = {col, row, value};
        A[col].push_back(e1);
        A[row].push_back(e2);
        B[row].push_back(e1);
        B[col].push_back(e2);
    }

    clock_t begin = clock();
    compute(n, m, A, B, C, thread_num);
    clock_t end = clock();
    double runtime = (double)(end - begin) / CLOCKS_PER_SEC;
    printf("Runime: %lf\n", runtime);
    return 0;
}