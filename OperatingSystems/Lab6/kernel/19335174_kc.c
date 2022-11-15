extern void cls();
extern char getChar();
extern void printChar();
extern void PowerOff();
extern void Reboot();
extern void int22h();
extern void loadProgram();
extern void loadReady();
extern void setIF();
extern int InitStack();

typedef struct {
	int ax;
	int bx;
	int cx;
	int dx;
	int di;
	int bp;
	int es;
	int ds;
	int si;
	int ss;
	int sp;
	int ip;
	int cs;
	int flags;
}cpuRegisters;

typedef struct {
	cpuRegisters cpu;
	int pid;
	char name[10];
	int state;/*三种状态：0进程空闲，1进程运行，2进程阻塞*/
}PCB;

PCB pcbList[5];/*创建一个最多有5个进程的PCB列表，最后一个为内核进程*/
PCB *curPCB = &pcbList[4];/*指向当前运行的PCB块*/
PCB *kerPCB = &pcbList[4];
int NumOfProcess = 0;
int MaxNumOfProcess = 5;
int i;

char x;
char command[20];
int symbol;
int tasks = 0;
char ttime[20] = "";
char ddate[20] = "";

void strcpy(char *a, char *b) {
	int i;
	for (i = 0; b[i] != 0; i++)
		a[i] = b[i];
	a[i] = 0;
}

int strcmp(char* a,char* b) {
    int i=0,j=0;
    while(a[i]!=0&&b[j]!=0) {
        if(a[i]!=b[j])
            return 1;
        i++;
        j++;
    }
    if(a[i]==0&&b[j]==0)
        return 0;
    else
        return 1;
}

void printf(char* str) {
    int i=0;
    while(str[i]) {
        printChar(str[i]);
        i++;
    }
}

/*初始化PCB列表*/
void InitPCB() {
	int i;
	for (i = 0; i < MaxNumOfProcess; i++)
		pcbList[i].state = 0;
	kerPCB->state = 1;
	kerPCB->pid = MaxNumOfProcess - 1;
	strcpy(kerPCB->name, "kernel");
}

/*进程调度*/
void schedule() {
	int i = (curPCB->pid + 1) % MaxNumOfProcess;
	if (NumOfProcess == 0) {
		curPCB = &pcbList[MaxNumOfProcess - 1];
		curPCB->state = 1;
		return;
	}
	while (i != curPCB->pid) {
		if (pcbList[i].state == 2) {
			curPCB->state = 2;
			pcbList[i].state = 1;
			curPCB = &pcbList[i];
			return;
		}
		i = (i + 1) % MaxNumOfProcess;
	}
}

/*进程创建，成功返回进程号pid，否则返回-1*/
int fork(int cs, int ip, int id, int num) {
	int i;
	for (i = 0; i < MaxNumOfProcess; i++)/*寻找空闲的PCB*/
		if (pcbList[i].state == 0)
			break;
	if (i == MaxNumOfProcess) {/*没有空闲PCB，进程创建失败*/
		printf("Fork failed\r\n");
		return 0;
	}
	pcbList[i].cpu.cs = cs;
	pcbList[i].cpu.ds = cs;
	pcbList[i].cpu.es = cs;
	pcbList[i].cpu.ip = ip;
	pcbList[i].cpu.ss = cs;
	pcbList[i].cpu.sp = InitStack(cs);/*初始化进程栈*/
	pcbList[i].cpu.flags = 512;
	pcbList[i].pid = i;
	pcbList[i].name[0] = '0' + i;
	pcbList[i].name[1] = 0;
	loadReady(cs);/*加载代码段前缀到指定的段*/
	loadProgram(cs, ip, id, num);/*加载用户程序到内存指定位置*/
	pcbList[i].state = 2;
	NumOfProcess += 1;
	return i;
}

/*结束进程*/
void endProcess() {
	NumOfProcess--;
	curPCB->state = 0;
	setIF();/*开中断*/
	while (1);/*阻塞至一个时间片结束*/
}

void Screen() {
    printf("********************************************************************************\n\r");
    printf("*                               Welcome to my OS!                              *\n\r");
    printf("*                                 STY 19335174                                 *\n\r");
	printf("*                                Enjoy yourself!                               *\n\r");
    printf("********************************************************************************\n\r");
    printf("Enter help to get the command list\n\r");
}

void help() {
    printf("\n\rhelp:           get the command list\n\r");
    printf("cls:            clear the screen\n\r");
	printf("run-:           run some user programs in parallel, such as 'run-1234'\n\r");
	printf("int22h:         print INT22H\n\r");
	printf("test:           run the libs program\n\r");
    printf("ls:             get the file list\n\r");
	printf("reboot:         restart the OS\n\r");
    printf("poweroff:       exit the OS\n\r");
}

void InputCom(char* command) {
    int i=0;
    getChar();
    while(x!=13) {
        if(x==8) {
            printChar(x);
            printChar(32);
            i--;
            printChar(x);
            getChar();
            continue;
        }
        printChar(x);
        command[i]=x;  
        i++;
        getChar();
    }
    command[i]='\0';
}

void file() {
    printf("\n\rThe Number Of Files: 5\n\r");
	printf("1.Number      402B\n\r");
	printf("2.Name        397B\n\r");
	printf("3.Rectangle   298B\n\r");
	printf("4.Stone       393B\n\r");
	printf("5.Test        867B\n\r");
}

void RunCom(char *command) {
	int i = 4;
    if(!strcmp(command,"help")) {
        help();
	}
    else if(!strcmp(command,"cls")) {
        cls();
	}
	else if(!strcmp(command,"ls")) {
        file();
	}
	else if(command[0]=='r'&&command[1]=='u'&&command[2]=='n'&&command[3]=='-') {
		while (command[i] == '1' || command[i] == '2' || command[i] == '3' || command[i] == '4') {
			if (command[i] == '1') fork(0x2000, 0x100, 2, 1);
			if (command[i] == '2') fork(0x3000, 0x100, 3, 1);
			if (command[i] == '3') fork(0x4000, 0x100, 4, 1);
			if (command[i] == '4') fork(0x5000, 0x100, 5, 1);
			i++;
		}
    }
	else if(!strcmp(command,"test")) {
		cls();
		fork(0x2000, 0x100, 6, 2);
		cls();
    }
	else if(!strcmp(command,"int22h")) {
        int22h();
	}
	else if(!strcmp(command,"reboot")) {
        Reboot();
	}
    else if(!strcmp(command,"poweroff")) {
        symbol = 0;
	}
	else {
		printf("\n\rWrong command!\n\r");
	}
	while (NumOfProcess != 0);/*阻塞，直至进程都完成*/
}

cmain(){
    cls();
	InitPCB();
    Screen();
    symbol = 1;
    while(symbol) {
		for (i = 0; i < MaxNumOfProcess - 1; i++)
			pcbList[i].state = 0;
		printf("\n\r>>");
        InputCom(command);
        RunCom(command);
    }
    cls();
    printf("Thank you for using!\n\r");
	printf("See you next time!\n\r");
	printf("Press any key to turn off the power...\n\r");
    getChar();
	PowerOff();
}