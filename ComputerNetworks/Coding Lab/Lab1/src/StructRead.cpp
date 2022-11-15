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

void PrintPerson(Person* per) {
	/* 读出并显示一个员工记录 */
	char regtime[TIME_BUF_LEN];
	char sendtime[TIME_BUF_LEN];
	// 显示员工记录
	printf("用户名： %s\r\n", per->username);    // 显示用户名
	printf("级别：%d\r\n", per->level);          // 显示级别
	printf("Email地址：%s\r\n", per->email);     // 显示email
	time_t t1 = (time_t)per->sendtime;
	ctime_s(sendtime, TIME_BUF_LEN, &t1);
	printf("发送时间：%s", sendtime);                  // 显示发送时间
	ctime_s(regtime, TIME_BUF_LEN, &per->regtime);
	printf("注册时间：%s", regtime);                   // 显示注册时间   
}

int main() {
	FILE* pFile;
	Person per;
	//打开要读取的二进制文件(r-read b-binary)
	if (fopen_s(&pFile, "e:\\temp\\Persons.stru", "rb") != NULL) {
		printf("读入文件未找到！\n");
		printf("按任意键继续...");
		getchar();
		getchar();
		exit(1);
	}
	while (fread(&per, sizeof(Person), 1, pFile) == 1) {
		PrintPerson(&per);
	}
	fclose(pFile);
	printf("\r\nPress any key to continue...");
	getchar();
	getchar();
	return 0;
}
