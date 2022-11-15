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

#define	LEN		2000  
#define WSVERS		MAKEWORD(2, 0)      
#pragma comment(lib,"ws2_32.lib")        

char* host;
int finish = 0;
bool download = false;
int dport = 0;

struct Sub {
    SOCKET control;
    string dest;
    Sub(SOCKET& s, string f) {
        control = s;
        dest = f;
    }
};

unsigned __stdcall fun(void* ptr) {
    char* ptr2;
    char buf[LEN];
    SOCKET s = reinterpret_cast<Sub*>(ptr)->control;
    FILE* file = NULL;
    memset(buf, 0, LEN);
    while (1) {
        int cc = recv(s, buf, LEN, 0);
        if (cc == SOCKET_ERROR || cc == 0) {
            printf("Error\n");
            return 1;
        }
        else {
            buf[cc] = '\0';
            printf("%s", buf);
            if (!strncmp(buf,"227",3)) {
                string p(buf);
                size_t pos1 = p.find_last_of(',');
                string port1 = p.substr(pos1 - 3, pos1 - 1);
                string port2 = p.substr(pos1 + 1, pos1 + 3);
                dport = _strtol_l(port1.c_str(), &ptr2, 10, NULL) * 256 + _strtol_l(port2.c_str(), &ptr2, 10, NULL);
                SOCKET dsocket;
                struct sockaddr_in dsin;	            /* an Internet endpoint address	*/
                WSADATA wsadata;
                WSAStartup(WSVERS, &wsadata);						   //加载winsock library。WSVERS为请求的版本，wsadata返回系统实际支持的最高版本
                dsocket = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);	    //创建套接字，参数：因特网协议簇(family)，流套接字，TCP协议
                memset(&dsin, 0, sizeof(dsin));
                dsin.sin_family = AF_INET;
                dsin.sin_addr.s_addr = inet_addr(host);
                dsin.sin_port = htons((u_short)dport);
                connect(dsocket, (struct sockaddr*)&dsin, sizeof(dsin));
                download = true;
                while (1) {
                    string x = reinterpret_cast<Sub*>(ptr)->dest;
                    while (_access(x.c_str(), 0) == 0);
                    file = fopen(x.c_str(), "wb");
                    if (file == NULL) {
                        printf("File can not find!\n");
                        printf("Please press any key to continue...");
                        getchar();
                        getchar();
                        exit(1);
                    }
                    printf("Start downloading...\n");
                    while (1) {
                        int cc2 = recv(dsocket, buf, LEN, 0);
                        int f = fwrite(buf, 1, cc2, file);
                        if (cc2 <= 0) break;
                    }
                    printf("Finish!\n");
                    fclose(file);
                    finish++;
                    memset(buf, 0, LEN);
                }
                download = false;
            }
        }
    }
    return 0;
}

int main(int argc, char* argv[]) {
    host = argv[1];	    /* server IP to connect         */
    const char* service = "21";  	    /* server port to connect       */
    string source;
    string dest;
    source = argv[2];
    dest = argv[3];
    struct sockaddr_in sin;	            /* an Internet endpoint address	*/
    SOCKET	sock;		  	            /* socket descriptor	    	*/

    WSADATA wsadata;
    WSAStartup(WSVERS, &wsadata);
    sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);

    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = inet_addr(host);
    sin.sin_port = htons((u_short)atoi(service));
    connect(sock, (struct sockaddr*)&sin, sizeof(sin));
    Sub s(sock, dest);
    HANDLE thread = (HANDLE)_beginthreadex(NULL, 0, &fun, (void*)&s, 0, NULL);
    string* command = new string[5];
    command[0] = "user net\r\n";
    command[1] = "pass 123456\r\n";
    command[2] = "pasv\r\n";
    command[3] = "retr " + source + "\r\n";
    command[4] = "quit\r\n";
    for (int j = 0; j < 5; j++) {
        if (command[j].substr(0, 4) == "retr")
            while (!download);
        if (command[j].substr(0, 4) == "quit")
            while (!finish);
        printf("%s", command[j].c_str());
        send(sock, command[j].c_str(), command[j].length(), 0);
        Sleep(50);
    }
    CloseHandle(thread);
    closesocket(sock);

    WSACleanup();
    printf("Please press any key to continue...");
    getchar();
    return 0;
}
