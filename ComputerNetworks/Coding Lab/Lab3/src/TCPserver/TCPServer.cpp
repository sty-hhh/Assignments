#include <stdlib.h>
#include <stdio.h>
#include <winsock2.h>
#include <time.h>
#include "conio.h"
#include <Windows.h>
#include <process.h>

#define BUFLEN 2000
#define	WSVERS	MAKEWORD(2, 0)

#pragma comment(lib,"ws2_32.lib")  //ʹ��winsock 2.2 library
struct	sockaddr_in fsin;	    //the from address of a client
SOCKET	msock, ssock;		    //master & slave sockets
WSADATA wsadata;
char* service = "50500";

int	    alen;			        //from-address length
char*	pts;						//pointer to time string
time_t	now;			        //current time
SOCKET sockets[BUFLEN];
HANDLE thread[BUFLEN];
unsigned int thread_id, Thread_id[BUFLEN], cnt;

unsigned int __stdcall server(void* p) {
	char buf[BUFLEN],buf2[BUFLEN];
	time_t time_now;
	char* pts;
	SOCKET sock = ssock;
	int now = cnt;
	sockets[now] = sock;
	Thread_id[now] = thread_id;

	(void)time(&time_now);
	pts = ctime(&time_now);

	sprintf(buf2, "ip: %s port: %d\ntime: %smessage: Enter!", inet_ntoa(fsin.sin_addr), fsin.sin_port, pts);
	printf("%s\n", buf2);
	for (int i = 0; i <= cnt; i++) {
		if (sockets[i] != NULL) {
			(void)send(sockets[i], buf2, strlen(buf2), 0);
		}
	}
	printf("\n");
	while (true) {
		int cc = recv(sock, buf, BUFLEN, 0);
		if (cc == SOCKET_ERROR) {
			sprintf(buf2, "ip: %s port: %d\ntime: %smessage: Leave!", inet_ntoa(fsin.sin_addr), fsin.sin_port, pts);
			printf("%s\n", buf2);
			(void)closesocket(sock);
			sock = NULL;
			sockets[now] = NULL;
			CloseHandle(thread[now]);;
			for (int i = 0; i <= cnt; i++) {
				if (sockets[i] != NULL) {
					(void)send(sockets[i], buf2, strlen(buf2), 0);
				}
			}
			printf("\n");
			break;
		}
		else if (cc > 0) {
			buf[cc] = '\0';
			sprintf(buf2, "ip: %s port: %d\ntime: %smessage: %s", inet_ntoa(fsin.sin_addr), fsin.sin_port, pts, buf);
			printf("%s\n", buf2);
			for (int i = 0; i <= cnt; i++) {
				if (sockets[i] != NULL) {
					(void)send(sockets[i], buf2, strlen(buf2), 0);
				}
			}
			printf("\n");
		}
	}
	return 0;
}

void
main(int argc, char *argv[]) 
{
	struct  sockaddr_in sin;	    //an Internet endpoint address		
	WSAStartup(WSVERS, &wsadata);						// ����winsock library��WSVERSָ������ʹ�õİ汾��wsadata����ϵͳʵ��֧�ֵ���߰汾
	msock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	// �����׽��֣�������������Э���(family)�����׽��֣�TCPЭ��
														// ���أ�Ҫ�����׽��ֵ���������INVALID_SOCKET
	cnt = -1;
	memset(&sin, 0, sizeof(sin));						// ��&sin��ʼ�ĳ���Ϊsizeof(sin)���ڴ���0
	sin.sin_family = AF_INET;							// ��������ַ��(INET-Internet)
	sin.sin_addr.s_addr = INADDR_ANY;					// ��������(�ӿڵ�)IP��ַ��
	sin.sin_port = htons((u_short)atoi(service));		// �����Ķ˿ںš�atoi--��asciiת��Ϊint��htons--������������(16λ)
	bind(msock, (struct sockaddr *)&sin, sizeof(sin));  // �󶨼�����IP��ַ�Ͷ˿ں�

	listen(msock, 5);                                   // �ȴ��������ӵĶ��г���Ϊ5
	printf("Command: TCPServer [Port]\n");
	printf("Default: TCPServer 50500\n\n");
    while(!_kbhit()){ 		                             // ����Ƿ��а���
       alen = sizeof(struct sockaddr);                   // ȡ����ַ�ṹ�ĳ���
	   ssock = accept(msock, (struct sockaddr *)&fsin, &alen); // ������µ��������󣬷��������׽��֣����򣬱�������fsin�����ͻ���IP��ַ�Ͷ˿ں�
	   thread[++cnt] = (HANDLE)_beginthreadex(NULL, 0, server, NULL, 0, &thread_id);
    }
    (void) closesocket(msock);                                 // �رռ����׽���
     WSACleanup();                                             // ж��winsock library
	 for (int i = 0; i <= cnt; i++)
		 if (thread[i] != NULL)
			 WaitForSingleObject(thread[i], INFINITE);
	 printf("���س�������...");
	 getchar();
}

