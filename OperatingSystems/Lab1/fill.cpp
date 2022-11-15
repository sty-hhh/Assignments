#include <stdio.h>
char s[] = "19335174STY", c[1440 << 10];
int main() {
	FILE* fp;
	fread(c, sizeof(*c), sizeof(c), fopen("E:\\styPC\\styPC_1.img", "rb+"));
	for (int i = 91; i < 510; ++i) {
		c[i] = s[i % (sizeof(s) - 1)];
	}
	fwrite(c, sizeof(*c), sizeof(c), fopen("E:\\styPC\\a.img", "wb"));
	return 0;
}
