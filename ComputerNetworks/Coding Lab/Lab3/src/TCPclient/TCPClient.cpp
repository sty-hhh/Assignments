#include <stdlib.h>
#include <stdio.h>
#include <winsock2.h>
#include <string.h>
#include <process.h>
#include <windows.h>

#define	BUFLEN		2000                  // ��������С
#define WSVERS		MAKEWORD(2, 0)        // ָ���汾2.0 
#pragma comment(lib,"ws2_32.lib")         // ʹ��winsock 2.0 Llibrary

SOCKET sock;
HANDLE thread;
unsigned thread_id;
unsigned int __stdcall client(void* p);

unsigned int __stdcall client(void* p) {
	char buf[BUFLEN];
	while (true) {
		int cc = recv(sock, buf, BUFLEN, 0);
		if (cc == SOCKET_ERROR || cc == 0) {
			printf("Error:%d\n��������Ͽ����ӣ�\n", GetLastError());
			CloseHandle(thread);
			(void)closesocket(sock);
			break;
		}
		else {
			buf[cc] = '\0';
			printf("%s\n\n", buf);
		}
	}
	return 0;
}

void main(int argc, char *argv[])
{
	char*	host = "172.26.98.190";		// server IP to connect   172.26.34.203
	char*	service = "50500";  	    // server port to connect
	struct sockaddr_in sin;	            // an Internet endpoint address	
	char	buf[BUFLEN+1];   		        // buffer for one line of text		    		    

	WSADATA wsadata;
	WSAStartup(WSVERS, &wsadata);						  //����winsock library��WSVERSΪ����İ汾��wsadata����ϵͳʵ��֧�ֵ���߰汾
  
	sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	  //�����׽��֣�������������Э���(family)�����׽��֣�TCPЭ��
														  //���أ�Ҫ�����׽��ֵ���������INVALID_SOCKET
	printf("Command: TCPClient [ServerIPAddress [Port]]\n");
    memset(&sin, 0, sizeof(sin));						  // ��&sin��ʼ�ĳ���Ϊsizeof(sin)���ڴ���0
    sin.sin_family = AF_INET;							  // ��������ַ��
    sin.sin_addr.s_addr = inet_addr(host);                // ������IP��ַ(32λ)
    sin.sin_port = htons((u_short)atoi(service));         // �������˿ں�  
    connect(sock, (struct sockaddr *)&sin, sizeof(sin));  // ���ӵ�������
	thread = (HANDLE)_beginthreadex(NULL, 0, client, NULL, 0, &thread_id);
	while (true) {
		scanf("%s",buf);
		if (!strcmp(buf, "exit")) break;
		(void)send(sock, buf, strlen(buf), 0);
	}
	CloseHandle(thread);
	closesocket(sock);
	WSACleanup();

	puts("���س�������...");
	getchar();
}