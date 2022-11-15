#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

int Global;
void *Thread1(void *x) {
    Global++;
    return NULL;
}
void *Thread2(void *x) {
    Global--;
    return NULL;
}

int main() {
    pthread_t *thread_handles = (pthread_t*)malloc(2*sizeof(pthread_t)); 
    pthread_create(&thread_handles[0], NULL, Thread1, NULL);  
    pthread_create(&thread_handles[1], NULL, Thread2, NULL);  
    pthread_join(thread_handles[0], NULL); 
    pthread_join(thread_handles[1], NULL); 
    free(thread_handles);
    return 0;
}