/* TCPServer.cpp - main */

#include <stdlib.h>
#include <stdio.h>
#include <winsock2.h>
#include <time.h>
#include "conio.h"

#define	WSVERS	MAKEWORD(2, 0)
#define BUFLEN 2000
#pragma comment(lib,"ws2_32.lib")  //ʹ��winsock 2.2 library
/*------------------------------------------------------------------------
 * main - Iterative TCP server for TIME service
 *------------------------------------------------------------------------
 */
void main(int argc, char *argv[]) 
/* argc: �����в��������� ���磺C:\> TCPServer 8080 
                     argc=2 argv[0]="TCPServer",argv[1]="8080" */
{
	struct	sockaddr_in fsin;	    /* the from address of a client	  */
	SOCKET	msock, ssock;		    /* master & slave sockets	      */
	WSADATA wsadata; 
	char	*service = "50500";
	struct  sockaddr_in sin;	    /* an Internet endpoint address		*/
    int	    alen;			        /* from-address length		        */
	char	*pts;			        /* pointer to time string	        */
	time_t	now;			        /* current time			            */
	char	buf[BUFLEN + 1];

	WSAStartup(WSVERS, &wsadata);						// ����winsock library��WSVERSָ������ʹ�õİ汾��wsadata����ϵͳʵ��֧�ֵ���߰汾
	msock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	// �����׽��֣�������������Э���(family)�����׽��֣�TCPЭ��
														// ���أ�Ҫ�����׽��ֵ���������INVALID_SOCKET

	memset(&sin, 0, sizeof(sin));						// ��&sin��ʼ�ĳ���Ϊsizeof(sin)���ڴ���0
	sin.sin_family = AF_INET;							// ��������ַ��(INET-Internet)
	sin.sin_addr.s_addr = INADDR_ANY;					// ��������(�ӿڵ�)IP��ַ��
	sin.sin_port = htons((u_short)atoi(service));		// �����Ķ˿ںš�atoi--��asciiת��Ϊint��htons--������������(host to network��s-short 16λ)
	bind(msock, (struct sockaddr *)&sin, sizeof(sin));  // �󶨼�����IP��ַ�Ͷ˿ں�

	listen(msock, 5);                                   // ��������Ϊ5������������У����ѵ������������������еȴ�������
	printf("��������������\n\n");

    while(!_kbhit()){ 		                                   // ����Ƿ��а���,���û�������ѭ����ִ��
       alen = sizeof(struct sockaddr);                         // ȡ����ַ�ṹ�ĳ���
	   ssock = accept(msock, (struct sockaddr *)&fsin, &alen); // ����������������������������������������󲢽������ӣ����ظ����ӵ��׽��֣����򣬱���䱻����ֱ�����зǿա�fsin�����ͻ���IP��ַ�Ͷ˿ں�
	   int ccc = recv(ssock, buf, BUFLEN, 0);

	   printf("�յ���Ϣ��%s\n", buf);
       (void) time(&now);                                      // ȡ��ϵͳʱ��
       pts = ctime(&now);                                      // ��ʱ��ת��Ϊ�ַ���
	   printf("�յ�ʱ�䣺%s", pts);
	   printf("�ͻ���IP��ַ��%d.%d.%d.%d\n", fsin.sin_addr.S_un.S_un_b.s_b1, fsin.sin_addr.S_un.S_un_b.s_b2, fsin.sin_addr.S_un.S_un_b.s_b3, fsin.sin_addr.S_un.S_un_b.s_b4);
	   printf("�ͻ��˶˿ںţ�%d\n\n", fsin.sin_port);
	   char total[BUFLEN + 1];
	   sprintf(total, "���ݣ�%s\nʱ�䣺%s�ͻ���IP��ַ��%d.%d.%d.%d\n�ͻ��˶˿ںţ�%d\n", buf, pts, fsin.sin_addr.S_un.S_un_b.s_b1, fsin.sin_addr.S_un.S_un_b.s_b2, fsin.sin_addr.S_un.S_un_b.s_b3, fsin.sin_addr.S_un.S_un_b.s_b4, fsin.sin_port);
       int cc = send(ssock, total, strlen(total), 0);              // �ڶ�������ָ���ͻ�����������������ΪҪ���͵��ֽ��������ĸ�����һ����0������ֵ��>=0 ʵ�ʷ��͵��ֽ�����0 �Է������رգ�SOCKET_ERROR ������
       
	   (void) closesocket(ssock);                              // �ر������׽���
     }
    (void) closesocket(msock);                                 // �رռ����׽���
     WSACleanup();                                             // ж��winsock library
     printf("���س�������...");
 	 getchar();										// �ȴ����ⰴ��
	 getchar();
}
