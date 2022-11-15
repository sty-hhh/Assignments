
; ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
;                              klib.asm
; ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

; 导入全局变量
extern _x
extern _str

;****************************
; SCOPY@                    *
;****************************
;局部字符串带初始化作为实参问题补钉程序
public SCOPY@
SCOPY@ proc 
		arg_0 = dword ptr 6
		arg_4 = dword ptr 0ah
		push bp
			mov bp,sp
		push si
		push di
		push ds
			lds si,[bp+arg_0]
			les di,[bp+arg_4]
			cld
			shr cx,1
			rep movsw
			adc cx,cx
			rep movsb
		pop ds
		pop di
		pop si
		pop bp
		retf 8
SCOPY@ endp

public _cls
_cls proc 
; 清屏
        push ax
        push bx
        push cx
        push dx		
			mov	ax, 600h	; AH = 6,  AL = 0
			mov	bx, 700h	; 黑底白字(BL = 7)
			mov	cx, 0		; 左上角: (0, 0)
			mov	dx, 184fh	; 右下角: (24, 79)
				int	10h		; 显示中断
			mov ah, 2
			mov bh, 0
			mov dx, 0
				int 10h
		pop dx
		pop cx
		pop bx
		pop ax
		ret
_cls endp

; 读取一个字符
public _getChar
_getChar proc
	mov ah,0
	int 16h
	mov byte ptr [_x],al
	ret
_getChar endp

; 输出一个字符
public _printChar
_printChar proc 
	push bp
	mov bp,sp
	mov al,[bp+4];char\ip\bp
	mov bl,0
	mov ah,0eh
	int 10h
	mov sp,bp
	pop bp
	ret
_printChar endp

;关机                
public _PowerOff
_PowerOff proc                  
	mov ax,5307H ;高级电源管理功能,设置电源状态 
	mov bx,0001H ;设备ID1:所有设备 
	mov cx,0003H ;状态3:表示关机 
	int 15H 
_PowerOff endp

;重启
public _Reboot
_Reboot proc                     
    mov al, 0FEh
    out 64h, al
    ret
_Reboot endp

;加载用户程序
OffSetOfUserPrg equ 8100h
public _loadUser
_loadUser proc
	push ax
	push bx
	push cx
	push dx
	push ds
	push es
	push bp
	;保护键盘中断
	xor ax, ax
	mov es, ax
	mov bp,offset saveplace
	mov word ptr ax,es:[4*9]
	mov word ptr [bp],ax
	mov word ptr ax,es:[4*9+2]
	mov word ptr [bp+2],ax 
	;修改键盘中断
	mov word ptr es:[4*9], offset OUCH
	mov word ptr es:[4*9+2], cs
	
	mov bp,sp
	mov ax,cs                ;段地址 ; 存放数据的内存基地址
	mov es,ax                ;设置段地址（不能直接mov es,段地址）
	mov bx, OffSetOfUserPrg  ;偏移地址; 存放数据的内存偏移地址
	mov ah,2                 ; 功能号
	mov al,1                 ;扇区数
	mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
	mov dh,0                 ;磁头号 ; 起始编号为0
	mov ch,0                 ;柱面号 ; 起始编号为0
	mov cl,[bp+16]           ;起始扇区号 ; 起始编号为1
	int 13H ;                调用读磁盘BIOS的13h功能
	;用户程序a.com已加载到指定内存区域
	call bx ;执行用户程序
	
	;恢复键盘中断
	xor ax, ax
	mov es, ax
	mov bp,offset saveplace
	mov word ptr ax,[bp]
	mov word ptr es:[4*9],ax
	mov word ptr ax,[bp+2]
	mov word ptr es:[4*9+2],ax

	pop bp
	pop es
	pop ds
	pop dx
	pop cx
	pop bx
	pop ax
	ret  ;中断用iret
_loadUser endp
saveplace dw 0,0

; 时钟中断处理程序
Timer:
	push ax
	push bx
	push ds			;保护寄存器
	push es
	
	mov ax,cs
	mov ds,ax
	lea bx,count	;判断count值是否为0，为0显示下一个"风火轮"
	mov al,[bx]
	dec al
	mov [bx],al
	cmp al,0
	jnz exit
	mov al,Delay
	mov [bx],al
	lea bx,wheel
	mov al,[bx]
	xor ah,ah
	inc ax
	cmp ax,4
	jnz next
	mov ax,1
next:
	mov [bx],al
	add bx,ax		;[bx]是要显示的字符，加上偏移量获取	
	mov ax,0b800h
	mov es,ax
	mov al,[bx]
	mov ah,0Fh		;黑底白字
	mov bx,((24*80+79)*2)	;24行79列
	mov es:[bx],ax
exit:
	mov al,20h		; AL = EOI
	out 20h,al		; 发送EOI到主8529A
	out 0A0h,al		; 发送EOI到从8529A
	
	pop es
	pop ds
	pop bx			;恢复寄存器
	pop ax
	iret			;中断返回

	Delay equ 5
	count label byte
		db Delay
	wheel label byte
		db 1
		db '|'
		db '/'
		db '\'

;键盘中断
OUCH:
    push ax			;保护寄存器							
	push bx
	push cx
	push dx
	push bp
    push es
	push ds
	push si
	
	mov ax,cs
	mov ds,ax	
	mov ax,0b800h
	mov es,ax
	lea si,len
	mov cx,[si]
	lea si,Message
	mov bx,(24*80+69)*2
	mov ah,07h

printOUCH:			;打印字符
	mov al,[si]
	mov es:[bx],ax
	inc si
	inc bx
	inc bx
	loop printOUCH
	
	mov ah,6		;清除该ouch
    mov al,0
	mov ch,24
	mov cl,69
	mov dh,24
	mov dl,79
	mov bh,7
	int 10H
    
    in al,60h
	mov al,20h		 ; AL = EOI
	out 20h,al		 ; 发送EOI到主8529A
	out 0A0h,al		 ; 发送EOI到从8529A

	pop si			 ;恢复寄存器
	pop ds
	pop es
	pop bp
	pop dx
	pop cx
	pop bx
	pop ax
	iret

	Message db "OUCH! OUCH!"
	len db 11