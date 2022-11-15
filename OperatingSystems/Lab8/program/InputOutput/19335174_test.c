#include"clibs.c"

int main() {
	char ch, str[80];
	int a;
	printf("ch=");
	getch(&ch);
	printf("str=");
	gets(str);
	printf("a=");
	scanf("%d", &a);
	putch(ch);
	printf("\r\n");
	puts(str);
	printf("\r\n");
	printf("ch=%c,a=%d,str=%s\r\n", ch, a, str);
	readch();/*用readch()按下任意键返回，否则会立即返回内核看不到输出结果*/
}