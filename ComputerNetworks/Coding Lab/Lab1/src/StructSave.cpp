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

int ReadPerson(Person* personSent) {
	char	pts[TIME_BUF_LEN];		   /* pointer to time string	        */
	time_t	now;			           /* current time			            */
	(void)time(&now);                   // ȡ��ϵͳʱ��
	ctime_s(pts, TIME_BUF_LEN, &now);   // ��ʱ��ת��Ϊ�ַ���
	char inputBuf[100];
	int inputNumber;
	/* ����Ա����¼ */
	printf("name: ");
	scanf_s("%s", inputBuf, USER_NAME_LEN);    // �����û���
	if (!strcmp(inputBuf, "exit")) return 0;
	strcpy_s(personSent->username, inputBuf);
	printf("level: ");
	scanf_s("%d", &inputNumber);               // �����û�����
	personSent->level = inputNumber;
	printf("email: ");
	scanf_s("%s", inputBuf, EMAIL_LEN);
	strcpy_s(personSent->email, inputBuf);     // ��������ʼ�
	personSent->sendtime = (DWORD)now;         // ���÷���ʱ��
	personSent->regtime = now;                 // ����ע��ʱ�� 
	printf("\n");
	return 1;
}

int main() {
	FILE* pFile;
	Person per;

	// ��Ҫд�Ķ������ļ�(w-write b-binary)��û���򴴽������򸲸�
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
