org  7c00h	;监控程序地址
OffsetOfUserPrg equ 8100h	;用户程序地址

Start:
	mov	ax, cs	     ; 置其他段寄存器值与CS相同
	mov	ds, ax	     ; 数据段
	mov	bp, Message	 ; BP=当前串的偏移地址
	mov	ax, ds		 ; ES:BP = 串地址
	mov	es, ax		 ; 置ES=DS	
cls:  		; 清屏
    mov ah,6
    mov al,0
    mov ch,0  
    mov cl,0
    mov dh,24  
    mov dl,79
    mov bh,7 
    int 10h	
show:
	mov	cx, MessageLength  ; CX = 串长（=9）
	mov	ax, 1301h	 ; AH = 13h（功能号）、AL = 01h（光标置于串尾）
	mov	bx, 0007h	 ; 页号为0(BH = 0) 黑底白字(BL = 07h)
    mov dh, 0		 ; 行号=0
	mov	dl, 0		 ; 列号=0
	int	10h		 ; BIOS的10h功能：显示一行字符

input:
    mov ah,0
    int 16h
    cmp al,'1'
    jz switch
    cmp al,'2'
    jz switch
    cmp al,'3'
    jz switch
    cmp al,'4'
    jz switch
    jmp input

switch:
    mov bl,'1'
    cmp al,bl
    jz program1
    mov bl,'2'
    cmp al,bl
    jz program2
    mov bl,'3'
    cmp al,bl
    jz program3
    mov bl,'4'
    cmp al,bl
    jz program4
    
program1:
    mov ax,cs                ;段地址 ; 存放数据的内存基地址
    mov es,ax                ;设置段地址（不能直接mov es,段地址）
    mov bx, OffsetOfUserPrg           ;偏移地址; 存放数据的内存偏移地址
    mov ah,2                 ;功能号，读磁盘
    mov al,1                 ;读入扇区数
    mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
    mov dh,0                 ;磁头号 ; 起始编号为0
    mov ch,0                 ;柱面号 ; 起始编号为0
    mov cl,2                 ;扇区号2
    int 13H ;                调用读磁盘BIOS的13h功能
    jmp OffsetOfUserPrg
program2:
    mov ax,cs                ;段地址 ; 存放数据的内存基地址
    mov es,ax                ;设置段地址（不能直接mov es,段地址）
    mov bx, OffsetOfUserPrg           ;偏移地址; 存放数据的内存偏移地址
    mov ah,2                 ;功能号，读磁盘
    mov al,1                 ;读入扇区数
    mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
    mov dh,0                 ;磁头号 ; 起始编号为0
    mov ch,0                 ;柱面号 ; 起始编号为0
    mov cl,3                 ;扇区号3
    int 13H ;                调用读磁盘BIOS的13h功能
    jmp OffsetOfUserPrg
program3:
    mov ax,cs                ;段地址 ; 存放数据的内存基地址
    mov es,ax                ;设置段地址（不能直接mov es,段地址）
    mov bx, OffsetOfUserPrg           ;偏移地址; 存放数据的内存偏移地址
    mov ah,2                 ;功能号，读磁盘
    mov al,1                 ;读入扇区数
    mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
    mov dh,0                 ;磁头号 ; 起始编号为0
    mov ch,0                 ;柱面号 ; 起始编号为0
    mov cl,4                 ;扇区号4
    int 13H ;                调用读磁盘BIOS的13h功能
    jmp OffsetOfUserPrg
program4:
    mov ax,cs                ;段地址 ; 存放数据的内存基地址
    mov es,ax                ;设置段地址（不能直接mov es,段地址）
    mov bx, OffsetOfUserPrg           ;偏移地址; 存放数据的内存偏移地址
    mov ah,2                 ;功能号，读磁盘
    mov al,1                 ;读入扇区数
    mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
    mov dh,0                 ;磁头号 ; 起始编号为0
    mov ch,0                 ;柱面号 ; 起始编号为0
    mov cl,5                 ;扇区号5
    int 13H ;                调用读磁盘BIOS的13h功能
    jmp OffsetOfUserPrg

Message:
    db "Welcome!",0AH,0DH
    db "Please Enter the number to choose the different program: ",0AH,0DH
    db "1.Number",0AH,0DH
    db "2.Name",0AH,0DH
    db "3.Rectangle",0AH,0DH
    db "4.Stone",0AH,0DH
    
    MessageLength  equ ($-Message)
	times 510-($-$$) db 0
    db 0x55,0xaa