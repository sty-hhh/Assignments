#include "clibs.c"

extern int fork();
extern void wait();
extern void exit();

char str[80];
int LetterNr = 0;
int DigitNr = 0;

void countLetter() {
	int i;
	for (i = 0; str[i] != 0; i++)
		if ((str[i] <= 'z' && str[i] >= 'a') || (str[i] <= 'Z' && str[i] >= 'A'))
			LetterNr++;
}

void countDigit() {
	int i;
	for (i = 0; str[i] != 0; i++)
		if (str[i] <= '9' && str[i] >= '0')
			DigitNr++;
}

int main() {
	int pid;
	printf("Input a string: ");
	scanf("%s", str);
	pid = fork();
	if (pid == -1) {
		printf("Fork failed!\r\n");
		exit();
	}
	if (pid) { /*父进程*/
		countLetter();
		wait();/*等待子进程*/
		printf("LetterNr = %d\r\n", LetterNr);
		printf("DigitNr = %d\r\n", DigitNr);
	}
	else { /*子进程*/
		countDigit();
		exit();
	}
}