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
	char username[USER_NAME_LEN];      // Ա����
	int level;                         // ���ʼ���
	char email[EMAIL_LEN];             // email��ַ
	DWORD sendtime;                    // ����ʱ��
	time_t regtime;                    // ע��ʱ��
} Person;

void PrintPerson(Person* per) {
	/* ��������ʾһ��Ա����¼ */
	char regtime[TIME_BUF_LEN];
	char sendtime[TIME_BUF_LEN];
	// ��ʾԱ����¼
	printf("�û����� %s\r\n", per->username);    // ��ʾ�û���
	printf("����%d\r\n", per->level);          // ��ʾ����
	printf("Email��ַ��%s\r\n", per->email);     // ��ʾemail
	time_t t1 = (time_t)per->sendtime;
	ctime_s(sendtime, TIME_BUF_LEN, &t1);
	printf("����ʱ�䣺%s", sendtime);                  // ��ʾ����ʱ��
	ctime_s(regtime, TIME_BUF_LEN, &per->regtime);
	printf("ע��ʱ�䣺%s", regtime);                   // ��ʾע��ʱ��   
}

int main() {
	FILE* pFile;
	Person per;
	//��Ҫ��ȡ�Ķ������ļ�(r-read b-binary)
	if (fopen_s(&pFile, "e:\\temp\\Persons.stru", "rb") != NULL) {
		printf("�����ļ�δ�ҵ���\n");
		printf("�����������...");
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
