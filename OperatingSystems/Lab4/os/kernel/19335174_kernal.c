extern void cls();
extern char getChar();
extern void printChar();
extern void loadUser();
extern void PowerOff();
extern void Reboot();

char x;
char *str;
char command[10];
int symbol;
int tasks;

void printf(char* str) {
    int i=0;
    while(str[i]) {
        printChar(str[i]);
        i++;
    }
}
void Screen() {
    printf("********************************************************************************\n\r");
    printf("*                               Welcome to my OS!                              *\n\r");
	printf("*                                Enjoy yourself!                               *\n\r");
    printf("*                                 STY 19335174                                 *\n\r");
    printf("********************************************************************************\n\r");
    printf("Enter help to get the command list\n\r");
}
void help() {
    printf("\n\rhelp:    get the command list\n\r");
    printf("cls:     clear the screen\n\r");
    printf("u1:      run the user program 1\n\r");
    printf("u2:      run the user program 2\n\r");
    printf("u3:      run the user program 3\n\r");
    printf("u4:      run the user program 4\n\r");
	printf("runall:  run all the user programs\n\r");
    printf("ls:      get the file list\n\r");
	printf("restart: restart the OS\n\r");
    printf("quit:    exit the OS\n\r");
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
    printf("\n\rThe Number Of Files: 4\n\r");
	printf("1.Number      402B\n\r");
	printf("2.Name        397B\n\r");
	printf("3.Rectangle   298B\n\r");
	printf("4.Stone       393B\n\r");
}
void RunCom(char *command) {
    if(!strcmp(command,"help")) 
        help();
    else if(!strcmp(command,"cls")) 
        cls();
	else if(!strcmp(command,"ls")) 
        file();
	else if(!strcmp(command,"u1")) {
        loadUser(2);
        cls();
    }
    else if(!strcmp(command,"u2")) {
        loadUser(3);
        cls();
    }
    else if(!strcmp(command,"u3")) {
        loadUser(4);
        cls();
    }
    else if(!strcmp(command,"u4")) {
        loadUser(5);
        cls();
    }
	else if(!strcmp(command,"runall")) {
        tasks = 4;
        cls();
    }
	else if(!strcmp(command,"restart")) 
        Reboot();
    else if(!strcmp(command,"quit")) 
        symbol=0;
	else 
		printf("\n\rWrong command!\n\r");
}

cmain(){
    cls();
    Screen();
    symbol=1;
    while(symbol) {  
		if (tasks!=0) {
			loadUser(6-tasks);
			tasks--;
			continue;
		}
		printf("\n\r>>");
        InputCom(command);
        RunCom(command);
    }
    cls();
    printf("\n\rThank you for using!\n\rSee you next time!\n\r");
    getChar();
	PowerOff();
}