#include <stdlib.h>
#include <stdio.h>
#include <winsock2.h>
#include <string.h>
#include <process.h>
#include <windows.h>

#define	BUFLEN		2000                  // 缓冲区大小
#define WSVERS		MAKEWORD(2, 0)        // 指明版本2.0 
#pragma comment(lib,"ws2_32.lib")         // 使用winsock 2.0 Llibrary

SOCKET sock;
HANDLE thread;
unsigned thread_id;
unsigned int __stdcall client(void* p);

unsigned int __stdcall client(void* p) {
	char buf[BUFLEN];
	while (true) {
		int cc = recv(sock, buf, BUFLEN, 0);
		if (cc == SOCKET_ERROR || cc == 0) {
			printf("Error:%d\n与服务器断开连接！\n", GetLastError());
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
	WSAStartup(WSVERS, &wsadata);						  //加载winsock library。WSVERS为请求的版本，wsadata返回系统实际支持的最高版本
  
	sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	  //创建套接字，参数：因特网协议簇(family)，流套接字，TCP协议
														  //返回：要监听套接字的描述符或INVALID_SOCKET
	printf("Command: TCPClient [ServerIPAddress [Port]]\n");
    memset(&sin, 0, sizeof(sin));						  // 从&sin开始的长度为sizeof(sin)的内存清0
    sin.sin_family = AF_INET;							  // 因特网地址簇
    sin.sin_addr.s_addr = inet_addr(host);                // 服务器IP地址(32位)
    sin.sin_port = htons((u_short)atoi(service));         // 服务器端口号  
    connect(sock, (struct sockaddr *)&sin, sizeof(sin));  // 连接到服务器
	thread = (HANDLE)_beginthreadex(NULL, 0, client, NULL, 0, &thread_id);
	while (true) {
		scanf("%s",buf);
		if (!strcmp(buf, "exit")) break;
		(void)send(sock, buf, strlen(buf), 0);
	}
	CloseHandle(thread);
	closesocket(sock);
	WSACleanup();

	puts("按回车键继续...");
	getchar();
}