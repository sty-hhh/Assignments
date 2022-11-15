/*程序源代码（fun.c）*/
extern char Message[];

fun(){
    int i=0,k=0;
    while(Message[i]) {
		if (Message[i]=='a') k++;
		i++;
    }
	Message[0]=k+'0';
}