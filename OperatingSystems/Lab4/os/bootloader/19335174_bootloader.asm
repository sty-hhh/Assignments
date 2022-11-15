org  7c00h					 ;BIOS将把引导扇区加载到0:7C00h处，并开始执行
OffsetOfMonitor equ 0A100h	 ;加载操作系统内核

ReadOs:
    mov ax,cs                ;段地址 ; 存放数据的内存基地址
    mov es,ax                ;设置段地址（不能直接mov es,段地址）
    mov bx, OffsetOfMonitor  ;存放内核的内存偏移地址OffsetOfMonitor
    mov ah,2                 ;功能号
    mov al,5                 ;扇区数，内核占用扇区数5
    mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
    mov dh,0                 ;磁头号 ; 起始编号为0
    mov ch,0                 ;柱面号 ; 起始编号为0
    mov cl,6                 ;存放内核的起始扇区号6
    int 13H 				 ;调用读磁盘BIOS的13h功能
    jmp 0a00h:100h			 ;控制权移交给内核

	times 510 - ($ - $$) db 0 ;将前510字节不是0就填0
	db 0x55, 0xaa