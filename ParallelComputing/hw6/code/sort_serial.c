#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void odd_even_sort(int *a, int n) {
    int phase, i, temp;
    for (phase = 0; phase < n; ++phase) {
        if (phase % 2 == 0) {
            for (int i = 1; i < n; i += 2)
                if (a[i-1] > a[i]) {
                    temp = a[i];
                    a[i] = a[i-1];
                    a[i-1] = temp;
                }
        }
        else {
            for (int i = 1; i < n-1; i += 2)
                if (a[i] > a[i+1]) {
                    temp = a[i];
                    a[i] = a[i+1];
                    a[i+1] = temp;
                }
        }
    }
}

int main() {
    int n;
    printf("Input array size:");
    scanf("%d", &n);
    int *a = malloc(n * sizeof(int));
    for (int i = 0; i < n; ++i) 
        a[i] = rand() % n;
    clock_t start = clock();
    odd_even_sort(a, n);
    clock_t end = clock();
    printf("Running time: %lf second\n", (double)(end - start)/CLOCKS_PER_SEC);
    // for (int i = 0; i < n; ++i) 
    //     printf("%d ", a[i]);
    // printf("\n");
}
