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

typedef struct {/*信号量*/
	int count;/*信号量的值*/
	PCB *next;/*阻塞队列*/
	char used;/*0表示未占用，1表示占用*/
}semaphone;

semaphone semList[10];/*信号量队列*/
PCB pcbList[10];/*创建一个最多有10个进程的PCB列表，最后一个为内核进程*/
PCB *curPCB = &pcbList[9];/*指向当前运行的PCB块*/
PCB *kerPCB = &pcbList[9];
char StackList[9][256];
int NumOfProcess = 0;
int MaxNumOfProcess = 10;
int NRsem = 10;
int StackSize = 0x100;

/*初始化PCB列表*/
void InitPCB() {
	int i;
	for (i = 0; i < MaxNumOfProcess; i++) {
		pcbList[i].state = NEW;
		pcbList[i].next = NEW;
	}
	kerPCB->state = RUNNING;
	kerPCB->pid = MaxNumOfProcess - 1;
	kerPCB->fid = MaxNumOfProcess - 1;
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
			if (curPCB->state == RUNNING)
				curPCB->state = READY;
			pcbList[i].state = RUNNING;
			curPCB = &pcbList[i];
			return;
		}
		i = (i + 1) % MaxNumOfProcess;
	}
}

/*进程创建，成功返回进程号pid，否则返回-1*/
int creatProcess(int head, int id, int num) {
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
	loadProgram(seg, 0x100, head, id, num);
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
	int num = curPCB->cpu.bx;/*派生的线程数*/
	while (i != curPCB->pid) {
		if (pcbList[i].state == NEW) {
			memcpy(&pcbList[curPCB->pid], &pcbList[i], sizeof(PCB));
			memcpy(StackList[curPCB->pid], StackList[i], StackSize);
			pcbList[i].state = READY;
			pcbList[i].fid = curPCB->pid;
			pcbList[i].pid = i;
			pcbList[i].cpu.sp += ((i - curPCB->pid) * StackSize);
			pcbList[i].cpu.ax = num;/*子进程的编号*/
			NumOfProcess++;
			num--;
			if (num == 0) {
				curPCB->cpu.ax = 0;/*父进程*/
				return;
			}
		}
		i = (i + 1) % MaxNumOfProcess;
	}
	curPCB->cpu.ax = -1;/*创建失败*/
}

void do_exit() {
	if (pcbList[curPCB->fid].state = BLOCKED)
		pcbList[curPCB->fid].state = READY;
	curPCB->state = NEW;
	NumOfProcess--;
	schedule();
}

void do_wait() {
	int i;
	for (i = 0; i < MaxNumOfProcess; ++i) {
		if (pcbList[i].state != NEW && pcbList[i].fid == curPCB->pid && i != curPCB->pid) { /*遍历所有子进程*/
			curPCB->state = BLOCKED;
			curPCB->cpu.ax = 0;
			schedule();
			return;
		}
	}
	curPCB->cpu.ax = -1;/*已无子进程，返回-1*/
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

void initSem() {
	int i;
	for (i = 0; i < NRsem; i++) {
		semList[i].used = 0;
		semList[i].next = 0;
	}
}

void do_GetSema() {
	int i;
	for (i = 0; i < NRsem; i++) {
		if (semList[i].used == 0) {
			semList[i].used = 1;
			semList[i].count = curPCB->cpu.bx;/*获取信号量初始值*/
			curPCB->cpu.ax = i;/*返回信号量编号*/
			return;
		}
	}
	curPCB->cpu.ax = -1;/*获取信号量失败*/
}

void do_FreeSema() {
	semList[curPCB->cpu.bx].used = 0;
}

void do_P() {
	semList[curPCB->cpu.bx].count--;/*信号量的值减1*/
	if (semList[curPCB->cpu.bx].count < 0) {
		curPCB->state = BLOCKED;/*阻塞当前进程*/
		curPCB->next = semList[curPCB->cpu.bx].next;/*加入阻塞队列*/
		semList[curPCB->cpu.bx].next = curPCB;
		schedule();/*调度进程*/
	}
}

void do_V() {
	PCB *temp;
	semList[curPCB->cpu.bx].count++;/*信号量的值加1*/
	if (semList[curPCB->cpu.bx].count <= 0) {
		temp = semList[curPCB->cpu.bx].next;
		semList[curPCB->cpu.bx].next = semList[curPCB->cpu.bx].next->next;
		temp->state = READY;/*从阻塞队列唤醒一个进程*/
	}
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
	printf("p1:             money-wrong\n\r");
    printf("p2:             money-right\n\r");
	printf("p3:             fruit\n\r");
    printf("p4:             writer-reader\n\r");
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
    printf("\n\rThe Number Of Files: 10\n\r");
	printf("01.Number          402B\n\r");
	printf("02.Name            397B\n\r");
	printf("03.Rectangle       298B\n\r");
	printf("04.Stone           393B\n\r");
	printf("05.Test            897B\n\r");
	printf("06.Count           959B\n\r");
	printf("07.money-wrong     1086B\n\r");
	printf("08.money-right     1148B\n\r");
	printf("09.fruit           1295B\n\r");
	printf("10.writer-reader   1475B\n\r");
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
			if (command[i] == '1') creatProcess(0, 2, 1);
			if (command[i] == '2') creatProcess(0, 3, 1);
			if (command[i] == '3') creatProcess(0, 4, 1);
			if (command[i] == '4') creatProcess(0, 5, 1);
			i++;
		}
    }
	else if(!strcmp(command,"test")) {
		creatProcess(0, 6, 2);
		cls();
    }
	else if(!strcmp(command,"count")) {
		creatProcess(0, 8, 2);
		cls();
    }
	else if(!strcmp(command,"p1")) {
		creatProcess(1, 1, 3);
		cls();
    }
	else if(!strcmp(command,"p2")) {
		creatProcess(1, 4, 3);
		cls();
    }
	else if(!strcmp(command,"p3")) {
		creatProcess(1, 7, 3);
		cls();
    }
	else if(!strcmp(command,"p4")) {
		creatProcess(1, 10, 3);
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
		initSem();
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