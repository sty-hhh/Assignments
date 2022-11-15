#include "clibs.c"

extern int fork();
extern void wait();
extern void exit();
extern void printf();
extern int GetSema();
extern void FreeSema();
extern void P();
extern void V();

int ReaderNum = 3;
int WriterNum = 2;
int reader_counter = 0;

int main() {
	int wmutex, rmutex, mutex;/*互斥量：写者、读者、读者和写者*/
	int pid, i;
	wmutex = GetSema(1);
	rmutex = GetSema(1);
	mutex = GetSema(1);
	pid = fork(ReaderNum + WriterNum);
	if (pid == -1) {
		printf("error in fork\r\n");
		return;
	}
	if (pid == 0) {/*父进程*/
		wait();
		FreeSema(wmutex);
		FreeSema(rmutex);
		FreeSema(mutex);
	}
	else if (pid >= 1 && pid <= ReaderNum) {/*读者*/
		for (i = 0; i < 2; i++) {
			P(rmutex);
			if (reader_counter == 0)
				P(mutex);/*写者写完，读者才能读*/
			reader_counter++;
			V(rmutex);
			printf("reader %d is reading, num of readers %d\r\n", pid - 1, reader_counter);
			P(rmutex);
			reader_counter--;
			if (reader_counter == 0)
				V(mutex);/*所有进入的读者都读完了，写者才能写*/
			V(rmutex);
		}
		exit();
	}
	else {/*写者*/
		for (i = 0; i < 3; i++) {
			P(wmutex);/*只有一个写者可以进入*/
			P(mutex);/*所有读者读完，才能写*/
			printf("writer %d is writing\r\n", pid - ReaderNum - 1);
			V(mutex);
			V(wmutex);
		}
		exit();
	}
}