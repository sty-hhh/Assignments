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

int i;
char x;
char command[20];
int symbol;
char ttime[20] = "";
char ddate[20] = "";

void strcpy(char *a, char *b) {
	int i;
	for (i = 0; b[i] != 0; i++)
		a[i] = b[i];
	a[i] = 0;
}

void memcpy(void *src, void *dest, int len) {
	char *s = (char *)src;
	char *d = (char *)dest;
	int i;
	for (i = 0; i < len; i++)
		d[i] = s[i];
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

int NEW = 0;
int RUNNING = 1;
int READY = 2;
int BLOCKED = 3;
int END = 4;

typedef struct stru{
	cpuRegisters cpu;
	int pid;
	int fid;/*父进程id*/
	char name[10];
	int state;/*五种状态*/
	struct stru *next;/*阻塞队列*/
}PCB;

PCB pcbList[10];
PCB *curPCB = &pcbList[9];/*指向当前运行的PCB块*/
PCB *kerPCB = &pcbList[9];
char StackList[9][256];/*程序的栈段*/
int StackSize = 0x100;
int NumOfProcess = 0;
int MaxNumOfProcess = 10;


/*初始化PCB列表*/
void InitPCB() {
	int i;
	for (i = 0; i < MaxNumOfProcess; i++)
		pcbList[i].state = NEW;
	kerPCB->state = RUNNING;
	kerPCB->pid = MaxNumOfProcess - 1;
	strcpy(kerPCB->name, "kernel");
}

/*进程调度*/
void schedule() {
	int i = (curPCB->pid + 1) % MaxNumOfProcess;
	if (NumOfProcess == 0) {
		curPCB = &pcbList[MaxNumOfProcess - 1];
		curPCB->state = RUNNING;
		return;
	}
	while (i != curPCB->pid) {
		if (pcbList[i].state == READY) {
			curPCB->state = READY;
			pcbList[i].state = RUNNING;
			curPCB = &pcbList[i];
			return;
		}
		i = (i + 1) % MaxNumOfProcess;
	}
}

/*进程创建，成功返回进程号pid，否则返回-1*/
int creatProcess(int id, int num) {
	int i, seg;
	for (i = 0; i < MaxNumOfProcess; i++)
		if (pcbList[i].state == NEW)
			break;
	if (i == MaxNumOfProcess) {
		printf("ERROR: Fail to creat process!\r\n");
		return 0;
	}
	seg = (i + 2) * 0x1000;
	pcbList[i].cpu.cs = seg;
	pcbList[i].cpu.ds = seg;
	pcbList[i].cpu.es = seg;
	pcbList[i].cpu.ip = 0x100;
	pcbList[i].cpu.ss = 0x1000;
	pcbList[i].cpu.sp = InitStack(&StackList[i][StackSize]);/*初始化进程栈*/
	pcbList[i].cpu.flags = 512;
	pcbList[i].pid = i;
	pcbList[i].fid = i;
	pcbList[i].name[0] = '0' + i;
	pcbList[i].name[1] = 0;
	loadReady(seg);
	loadProgram(seg, 0x100, id, num);
	pcbList[i].state = READY;
	NumOfProcess += 1;
	return i;
}

/*结束进程*/
void endProcess() {
	NumOfProcess--;
	curPCB->state = END;
	setIF();/*开中断*/
	while (1);/*阻塞至一个时间片结束*/
}

void do_fork() {
	int i = (curPCB->pid + 1) % MaxNumOfProcess;
	while (i != curPCB->pid) {
		if (pcbList[i].state == NEW) {
			memcpy(&pcbList[curPCB->pid], &pcbList[i], sizeof(PCB));/*save父进程*/
			memcpy(StackList[curPCB->pid], StackList[i], StackSize);/*子进程copy父进程*/
			pcbList[i].state = READY;
			pcbList[i].fid = curPCB->pid;
			pcbList[i].pid = i;
			pcbList[i].cpu.sp += ((i - curPCB->pid) * StackSize);
			pcbList[i].cpu.ax = 0;/*子进程*/
			curPCB->cpu.ax = 1;/*父进程*/
			NumOfProcess++;
			break;
		}
		i = (i + 1) % MaxNumOfProcess;
	}
	if (i == curPCB->pid)
		curPCB->cpu.ax = -1;/*创建失败*/
}

void do_exit() {
	pcbList[curPCB->fid].state = READY;
	curPCB->state = END;
	NumOfProcess--;
	setIF();
	while (1);
}

void do_wait() {
	curPCB->state = BLOCKED;
	schedule();
}

void block(int p) {
	curPCB->state = BLOCKED;
	curPCB->next = pcbList[p].next;
	pcbList[p].next = curPCB;
	schedule();
}

void wakeup(int p) {
	curPCB->state = READY;
	pcbList[p].next = curPCB->next;
}

void sleep() {
	curPCB->state = BLOCKED;
	schedule();
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
	printf("count:          run the count program\n\r");
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
	printf("5.Test        897B\n\r");
	printf("6.Count       959B\n\r");
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
			if (command[i] == '1') creatProcess(2, 1);
			if (command[i] == '2') creatProcess(3, 1);
			if (command[i] == '3') creatProcess(4, 1);
			if (command[i] == '4') creatProcess(5, 1);
			i++;
		}
    }
	else if(!strcmp(command,"test")) {
		cls();
		creatProcess(6, 2);
		cls();
    }
	else if(!strcmp(command,"count")) {
		cls();
		creatProcess(8, 2);
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
    Screen();
    symbol = 1;
    while(symbol) {
		InitPCB();
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