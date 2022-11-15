#include "clibs.c"

extern int fork();
extern void wait();
extern void exit();
extern void printf();
extern int GetSema();
extern void FreeSema();
extern void P();
extern void V();

void strcpy(char *a, char *b) {
	int i;
	for (i = 0; b[i] != 0; i++)
		a[i] = b[i];
	a[i] = 0;
}

char words[80];/*祝福，word[0]==0时表示无祝福*/

int main() {
	int pid, i;
	int fs, ws;/*两个信号量，代表水果与祝福*/
	int fruit = 0;/*0表示空，1表示苹果，2表示香蕉*/
	words[0] = 0;
	fs = GetSema(1);
	ws = GetSema(1);
	pid = fork(2);
	if (pid == -1) {
		printf("error in fork\r\n");
		return;
	}
	if (pid == 0) {/*父亲*/
		for (i = 0; i < 5; i++) {
			P(ws);
			P(fs);
			if (words[0] == 0 || fruit == 0)
				i--;
			else {/*祝福和水果都送齐了父亲才能享受*/
				if (fruit == 1)
					printf("words: %s fruit: apple\r\n", words);
				else
					printf("words: %s fruit: banana\r\n", words);
				words[0] = 0;/*取走祝福和水果*/
				fruit = 0;
			}
			V(fs);
			V(ws);
		}
		wait();
		FreeSema(fs);
		FreeSema(ws);
	}
	else if (pid == 1) {/*大儿子送祝福*/
		for (i = 0; i < 5; i++) {
			P(ws);
			if (words[0] != 0)
				i--;
			else
				strcpy(words, "Father will live one year after anther for ever!");
			V(ws);
		}
		exit();
	}
	else if (pid == 2) {/*小儿子送水果*/
		for (i = 0; i < 5; i++) {
			P(fs);
			if (fruit != 0)
				i--;
			else
				fruit = i % 2 + 1;
			V(fs);
		}
		exit();
	}
}