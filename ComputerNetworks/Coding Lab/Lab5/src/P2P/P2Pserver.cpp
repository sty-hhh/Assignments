#include <stdio.h>
#include <stdlib.h>
#include <io.h>
#include <iostream>
#include <winsock2.h>
#include <string.h>
#include <windows.h>
#include <math.h>
#include <ws2tcpip.h>
#include <process.h>
using namespace std;

#define	LEN		2000                  // ���ջ�������С
#define WSVERS	MAKEWORD(2, 0)        // ָ���汾2.0 
#pragma comment(lib,"ws2_32.lib")         // ʹ��winsock 2.0 Llibrary

struct MyFile {
	char name[LEN];
	long size;
};
WSADATA wsadata;
struct sockaddr_in fsin;	            /* an Internet endpoint address	*/
HANDLE thread;
int	cc;			                    /* recv character count		    */
SOCKET	msock, sock;		  	            /* socket descriptor	    	*/
char path[LEN];
char in[LEN];   //���������
char* ss;        //��������

unsigned __stdcall fun(void* x) {
	FILE* file = NULL;
	char buf[LEN];
	memset(buf, 0, LEN);
	while (1) {
		char type;
		cc = recv(sock, &type, 1, 0);
		if (type == 1) {
			MyFile  f;
			cc = recv(sock, (char*)&f, sizeof(MyFile), 0);
			char* ptr = strrchr(f.name, '\\');
			string x = path;
			string y = ptr;
			x += y;
			int count = 1;
			while (access(x.c_str(), 0) == 0) {
				string s = "(0)";
				s[1] += count;
				int pos = x.rfind('.');
				string pathname = x.substr(0, pos);
				string type = x.substr(pos, x.length() - pos);
				pos = x.rfind('(');
				pathname = pathname.substr(0, pos);
				pathname += s;
				pathname += type;
				x = pathname;
				count++;
			}
			if (fopen_s(&file, x.c_str(), "wb") != NULL) {
				printf("�ļ������ڣ�\n");
				getchar();
				getchar();
				exit(1);
			}
			long sum = 0;
			while (f.size - sum >= LEN) {
				cc = recv(sock, buf, LEN, 0);
				int len = fwrite(buf, 1, cc, file);
				sum += len;
			}
			cc = recv(sock, buf, f.size - sum, 0);
			fwrite(buf, 1, cc, file);
			if (cc <= 0) {
				printf("Error: %d.\n", GetLastError());
				return 1;
			}
			printf("�յ��ļ���%s\n", ptr + 1);
			fclose(file);
		}
		else {
			MyFile f;
			cc = recv(sock, (char*)&f, sizeof(MyFile), 0);
			cc = recv(sock, buf, f.size, 0);
			if (cc <= 0) {
				printf("Error: %d.\n", GetLastError());
				return 1;
			}
			buf[cc] = '\0';
			printf("%s\n", buf);
		}
	}
	return 0;
}

void main(int argc, char* argv[]) {
	const char* service = "50500"; 	    /* server port to connect       */

	struct  sockaddr_in sin;							  //an Internet endpoint address
	WSAStartup(WSVERS, &wsadata);						  //����winsock library��WSVERSΪ����İ汾��wsadata����ϵͳʵ��֧�ֵ���߰汾
	msock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	  //�����׽��֣�������������Э���(family)�����׽��֣�TCPЭ��

	FILE* file = NULL;
	char* fname = new char[LEN];

	memset(&sin, 0, sizeof(sin));						// ��&sin��ʼ�ĳ���Ϊsizeof(sin)���ڴ���0
	sin.sin_family = AF_INET;							// ��������ַ��(INET-Internet)
	sin.sin_addr.s_addr = INADDR_ANY;					// ��������(�ӿڵ�)IP��ַ��
	sin.sin_port = htons((u_short)atoi(service));		// �����Ķ˿ںš�atoi--��asciiת��Ϊint��htons--������������(16λ)
	bind(msock, (struct sockaddr*)&sin, sizeof(sin));  // �󶨼�����IP��ַ�Ͷ˿ں�
	listen(msock, 5);                                   // �ȴ��������ӵĶ��г���Ϊ10

	int alen = sizeof(struct sockaddr);                   // ȡ����ַ�ṹ�ĳ���
	sock = accept(msock, (struct sockaddr*)&fsin, &alen); // ������µ��������󣬷��������׽��֣����򣬱�������fsin�����ͻ���IP��ַ�Ͷ˿ں�	
	thread = (HANDLE)_beginthreadex(NULL, 0, &fun, NULL, 0, NULL);
	printf("������������\n");

	while (1) {
		printf(">>");
		gets_s(in);
		if (strcmp(in, "")) {
			ss = strtok(in, " ");
			if (strcmp(ss, "rdir") == 0) {
				char* x = strtok(NULL, " ");
				string a = x;
				memcpy(path, a.c_str(), a.length());
			}
			else if (strcmp(ss, "chat") == 0) {
				char* m = strtok(NULL, " ");
				char type = 2;
				MyFile f;
				memset(f.name, 0, LEN);
				f.size = strlen(m);
				send(sock, &type, 1, 0);
				send(sock, (char*)&f, sizeof(MyFile), 0);
				send(sock, m, strlen(m), 0);
			}
			else if (strcmp(ss, "send") == 0) {
				fname = strtok(NULL, " ");
				MyFile f;
				char buf[LEN];
				int len;
				if (fopen_s(&file, fname, "rb") != NULL) {
					printf("�ļ�δ�ҵ���\n");
					break;
				}
				char type = 1;
				strcpy(f.name, fname);
				fseek(file, 0, SEEK_END);
				f.size = ftell(file);
				fseek(file, 0, SEEK_SET);
				send(sock, &type, 1, 0);
				send(sock, (char*)&f, sizeof(MyFile), 0);
				while ((len = fread(buf, 1, LEN, file)) >= LEN)
					send(sock, buf, len, 0);
				send(sock, buf, len, 0);
			}
			else if (strcmp(ss, "quit") == 0) {
				printf("�ͻ������˳�\n");
				break; 
			}
			else {
				printf("��������\n");
			}
		}
	}
	CloseHandle(thread);
	shutdown(sock, SD_BOTH);
	WSACleanup();                                  // ж��winsock library
	printf("���س�������...");
	getchar();										// �ȴ����ⰴ��
}
