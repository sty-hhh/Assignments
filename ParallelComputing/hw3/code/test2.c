#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

pthread_mutex_t mutex;
int Global;

void *Thread1(void *x) {
    pthread_mutex_lock(&mutex);
    Global++;
    pthread_mutex_unlock(&mutex);
    return NULL;
}
void *Thread2(void *x) {
    pthread_mutex_lock(&mutex);
    Global--;
    pthread_mutex_unlock(&mutex);
    return NULL;
}

int main() {
    pthread_t *thread_handles = (pthread_t*)malloc(2*sizeof(pthread_t)); 
    pthread_mutex_init(&mutex, NULL);
    pthread_create(&thread_handles[0], NULL, Thread1, NULL);  
    pthread_create(&thread_handles[1], NULL, Thread2, NULL);  
    pthread_join(thread_handles[0], NULL); 
    pthread_join(thread_handles[1], NULL); 
    pthread_mutex_destroy(&mutex);
    free(thread_handles);
    return 0;
}