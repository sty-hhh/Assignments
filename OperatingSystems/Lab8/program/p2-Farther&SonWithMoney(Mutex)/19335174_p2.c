#include "clibs.c"

extern int fork();
extern void wait();
extern void exit();
extern void printf();
extern int GetSema();
extern void FreeSema();
extern void P();
extern void V();

void delay() {
	int i = 0;
	int j = 0;
	while (i < 10000) {
		i++;
		j = 0;
		while (j < 10000)
			j++;
	}
}


int main() {
	int pid, i, t, s;
	int totalSave = 0, totalDraw = 0;
	int bankBalance = 1000;
	s = GetSema(1);
	pid = fork(1);
	if (pid == -1) {
		printf("error in fork\r\n");
		return;
	}
	if (pid == 0) {/*父进程存钱，每次10元*/
		for (i = 0; i < 5; i++) {
			P(s);
			t = bankBalance;
			delay();
			t += 10;
			delay();
			bankBalance = t;
			totalSave += 10;
			printf("bankBalance=%d,totalSave=%d\r\n", bankBalance, totalSave);
			V(s);
		}
		wait();
		FreeSema(s);
	}
	else if (pid == 1) {/*子进程取钱，每次20元*/
		for (i = 0; i < 5; i++) {
			P(s);
			t = bankBalance;
			delay();
			t -= 20;
			delay();
			bankBalance = t;
			totalDraw += 20;
			printf("bankBalance=%d,totalDraw=%d\r\n", bankBalance, totalDraw);
			V(s);
		}
		exit();
	}
}