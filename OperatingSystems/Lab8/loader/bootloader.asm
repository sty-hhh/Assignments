org  7c00h					 ;BIOS将把引导扇区加载到0:7C00h处，并开始执行

ReadOs:
    mov ax,SegOfKernal       		;段地址 ; 存放数据的内存基地址
    mov es,ax                		;设置段地址（不能直接mov es,段地址）
    mov bx,OffSetOfKernal    		;存放内核的内存偏移地址OffsetOfMonitor
    mov ah,2                 		;功能号
    mov al,11                 		;扇区数，内核占用扇区数11
    mov dl,0                 		;驱动器号 ; 软盘为0，硬盘和U盘为80H
    mov dh,0                 		;磁头号 ; 起始编号为0
    mov ch,1                 		;柱面号 ; 起始编号为0
    mov cl,1                 		;存放内核的起始扇区号1
    int 13H 				 		;调用读磁盘BIOS的13h功能
    jmp SegOfKernal:OffSetOfKernal	;控制权移交给内核
	
	times 510 - ($ - $$) db 0 ;将前510字节不是0就填0
	OffSetOfKernal equ 100h
	SegOfKernal equ 1000h  ;第二个64k内存的段地址  0x1000
	db 0x55, 0xaa