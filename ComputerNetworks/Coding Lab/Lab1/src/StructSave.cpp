#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#define FNAME_LEN 300
#define USER_NAME_LEN 20
#define EMAIL_LEN 80
#define TIME_BUF_LEN 30
typedef unsigned long DWORD;

typedef struct {
	char username[USER_NAME_LEN];      // 员工名
	int level;                         // 工资级别
	char email[EMAIL_LEN];             // email地址
	DWORD sendtime;                    // 发送时间
	time_t regtime;                    // 注册时间
} Person;

int ReadPerson(Person* personSent) {
	char	pts[TIME_BUF_LEN];		   /* pointer to time string	        */
	time_t	now;			           /* current time			            */
	(void)time(&now);                   // 取得系统时间
	ctime_s(pts, TIME_BUF_LEN, &now);   // 把时间转换为字符串
	char inputBuf[100];
	int inputNumber;
	/* 输入员工记录 */
	printf("name: ");
	scanf_s("%s", inputBuf, USER_NAME_LEN);    // 输入用户名
	if (!strcmp(inputBuf, "exit")) return 0;
	strcpy_s(personSent->username, inputBuf);
	printf("level: ");
	scanf_s("%d", &inputNumber);               // 输入用户级别
	personSent->level = inputNumber;
	printf("email: ");
	scanf_s("%s", inputBuf, EMAIL_LEN);
	strcpy_s(personSent->email, inputBuf);     // 输入电子邮件
	personSent->sendtime = (DWORD)now;         // 设置发送时间
	personSent->regtime = now;                 // 设置注册时间 
	printf("\n");
	return 1;
}

int main() {
	FILE* pFile;
	Person per;

	// 打开要写的二进制文件(w-write b-binary)，没有则创建，有则覆盖
	if ((fopen_s(&pFile, "e:\\temp\\Persons.stru", "wb")) != NULL) {
		printf("cant open the file!\n");
		getchar();
		exit(0);
	}

	while (true) {
		if (!ReadPerson(&per)) break;
		if (fwrite(&per, sizeof(Person), 1, pFile) != 1) {
			printf("file write error!\n");
		}
	}
	fclose(pFile);
	printf("struct copy finished!\n");
	printf("press any key to continue...");
	getchar();
	return 0;
}
