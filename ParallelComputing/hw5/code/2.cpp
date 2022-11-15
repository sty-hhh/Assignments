#include <stdio.h>
#include <queue>
#include <omp.h>
#include <unistd.h>
#include <semaphore.h>
#define MaxSize 20
using namespace std;

queue<int> resources;
sem_t n ,s;

void producer(int id){
    int x;
    if (resources.empty())
        x = 1;
    else
        x = resources.back() + 1;
    if (x == MaxSize)
        return;
    sem_wait(&s);
    resources.push(x);
    sem_post(&s);
    sem_post(&n);
	printf("%d is produced by thread %d.\n", x, id);
}

void consumer(int id){
    sem_wait(&n);
    sem_wait(&s);
    int x = resources.front();
    resources.pop();  
    sem_post(&s); 
    printf("%d is consumed by thread %d.\n", x, id);
}

int main() {
    sem_init(&n, 0, 0);
    sem_init(&s, 0, 1);
    int producers = 4;
    int consumers = 2;

#   pragma omp parallel num_threads(producers+consumers) 
    {
        while (true) {
	        int id = omp_get_thread_num();
#           pragma omp parallel sections 
            {
#               pragma omp section 
                {
	                if (id < producers)
		                producer(id);
		        }
#               pragma omp section 
                {
		            if (id >= producers)
		                consumer(id);
		        }   
	        }
        }
	}
}
