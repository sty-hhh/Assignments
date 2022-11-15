#include <stdlib.h>
#include <stdio.h>
#include <winsock2.h>
#include <time.h>
#include "conio.h"
#include <Windows.h>
#include <process.h>

#define BUFLEN 2000
#define	WSVERS	MAKEWORD(2, 0)

#pragma comment(lib,"ws2_32.lib")  //使用winsock 2.2 library
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
	WSAStartup(WSVERS, &wsadata);						// 加载winsock library。WSVERS指明请求使用的版本。wsadata返回系统实际支持的最高版本
	msock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	// 创建套接字，参数：因特网协议簇(family)，流套接字，TCP协议
														// 返回：要监听套接字的描述符或INVALID_SOCKET
	cnt = -1;
	memset(&sin, 0, sizeof(sin));						// 从&sin开始的长度为sizeof(sin)的内存清0
	sin.sin_family = AF_INET;							// 因特网地址簇(INET-Internet)
	sin.sin_addr.s_addr = INADDR_ANY;					// 监听所有(接口的)IP地址。
	sin.sin_port = htons((u_short)atoi(service));		// 监听的端口号。atoi--把ascii转化为int，htons--主机序到网络序(16位)
	bind(msock, (struct sockaddr *)&sin, sizeof(sin));  // 绑定监听的IP地址和端口号

	listen(msock, 5);                                   // 等待建立连接的队列长度为5
	printf("Command: TCPServer [Port]\n");
	printf("Default: TCPServer 50500\n\n");
    while(!_kbhit()){ 		                             // 检测是否有按键
       alen = sizeof(struct sockaddr);                   // 取到地址结构的长度
	   ssock = accept(msock, (struct sockaddr *)&fsin, &alen); // 如果有新的连接请求，返回连接套接字，否则，被阻塞。fsin包含客户端IP地址和端口号
	   thread[++cnt] = (HANDLE)_beginthreadex(NULL, 0, server, NULL, 0, &thread_id);
    }
    (void) closesocket(msock);                                 // 关闭监听套接字
     WSACleanup();                                             // 卸载winsock library
	 for (int i = 0; i <= cnt; i++)
		 if (thread[i] != NULL)
			 WaitForSingleObject(thread[i], INFINITE);
	 printf("按回车键继续...");
	 getchar();
}

