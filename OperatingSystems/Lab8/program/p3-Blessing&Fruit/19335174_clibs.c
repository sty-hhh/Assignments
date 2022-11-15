extern char readch(void);
extern void putch(char c);

char x;
char snum[6];

void puts(char *s) {
	int i;
	for (i = 0; s[i] != 0; i++)
		putch(s[i]);
}
void getch(char *c) {
	char t = 0;
	x = 0;
	while (1) {
		t = x;
		readch();
		if(x == 8) {
            putCh(x);
            putCh(32);
            putch(x);
            continue;
        }
		if (x == 13) {/*回车*/
			x = t;
			putch(10);/*换行*/
			putch(13);
			break;
		}
		putch(x);
	}
	*c = x;
}
void gets(char* s) {
    int i = 0;
    readch();
    while(x != 13) {
        if(x == 8) {
            putCh(x);
            putCh(32);
            i--;
            putch(x);
            readch();
            continue;
        }
        putch(x);
		s[i] = x;  
        i++;
        readch();
    }
	putch(10);
	putch(13);
	s[i] = '\0';
}
/*把整数变成字符串*/
char *itoa(int n) {
	int i = 0, t = 10, s = 0;
	if (n == 0) {
		snum[0] = '0';
		snum[1] = 0;
		return snum;
	}
	while (n != 0) {
		snum[i] = n % t + '0';
		n /= 10;
		i++;
		s++;
	}
	for (i = 0; i < s / 2; i++) {
		char temp = snum[i];
		snum[i] = snum[s - 1 - i];
		snum[s - 1 - i] = temp;
	}
	snum[s] = 0;
	return snum;
}
/*把字符串变成整数*/
int atoi(void) {
	int i, s = 0;
	for (i = 0; snum[i] != 0; i++) {
		s *= 10;
		s += (snum[i] - '0');
	}
	return s;
}
void printf(char *str, ...) {
	int i;
	int offset = 1;
	for (i = 0; str[i] != 0; i++) {
		if (str[i] != '%')
			putch(str[i]);
		else {
			i++;
			switch (str[i]) {
				case 'd':
					puts(itoa((int)*(&str + offset)));
					break;
				case 'c':
					putch((char)*(&str + offset));
					break;
				case 's':
					puts((char *)*(&str + offset));
					break;
				default:
					continue;
			}
			offset += 1;
		}
	}
}
void scanf(char *str, ...) {
	int i;
	int offset = 1;
	for (i = 0; str[i] != 0; i++) {
		if (str[i] == '%') {
			i++;
			switch (str[i]) {
				case 'd':
					gets(snum);
					*((int *)(*(&str + offset))) = atoi();
					break;
				case 'c':
					getch((char *)*(&str + offset));
					break;
				case 's':
					gets((char *)*(&str + offset));
					break;
				default:
					continue;
			}
			offset += 1;
		}
	}
}