;BIOS基础系统调用

; 导入全局变量
extern _x
extern _current
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

; 输出一个字符
public _printChar
_printChar proc 
	mov ah,0
	int 21h
	ret
_printChar endp

; 读取一个字符
public _getChar
_getChar proc
	mov ah,1
    int 21h
	mov byte ptr [_x],al
	ret
_getChar endp

; 清屏
public _cls
_cls proc 
	mov ah,2
	int 21h
	ret
_cls endp

; 关机                
public _PowerOff
_PowerOff proc                  
	mov ah,3
	int 21h
	ret
_PowerOff endp

;重启
public _Reboot
_Reboot proc                     
    mov ah,4
	int 21h
	ret
_Reboot endp

;加载用户程序
OffSetOfUserPrg equ 8100h
public _loadUser
_loadUser proc
	push ax
	push ds
	push es
	push bp
	
	mov bp,sp
	mov ax,cs                ;段地址 ; 存放数据的内存基地址
	mov es,ax                ;设置段地址（不能直接mov es,段地址）
	mov bx, OffSetOfUserPrg  ;偏移地址; 存放数据的内存偏移地址
	mov ah,2                 ; 功能号
	mov al,1                 ;扇区数
	mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
	mov dh,0                 ;磁头号 ; 起始编号为0
	mov ch,0                 ;柱面号 ; 起始编号为0
	mov cl,[bp+10]           ;起始扇区号 ; 起始编号为1
	int 13H ;                调用读磁盘BIOS的13h功能
	;用户程序a.com已加载到指定内存区域
	call bx ;执行用户程序
	
	pop bp
	pop es
	pop ds
	pop ax
	ret  
_loadUser endp

;加载新的用户程序test.com
public _loadTest
_loadTest proc
	push ax
	push ds
	push es
	push bp
	
	mov bp,sp
	mov ax,2000h             ;段地址 ; 存放数据的内存基地址
	mov es,ax                ;设置段地址（不能直接mov es,段地址）
	mov bx,100h				 ;偏移地址; 存放数据的内存偏移地址
	mov ah,2                 ;功能号2
	mov al,2                 ;扇区数2
	mov dl,0                 ;驱动器号 ; 软盘为0，硬盘和U盘为80H
	mov dh,0                 ;磁头号 ; 起始编号为0
	mov ch,0                 ;柱面号 ; 起始编号为0
	mov cl,[bp+10]           ;起始扇区号 ; 起始编号为1
	int 13H ;                调用读磁盘BIOS的13h功能
	;用户程序test.com已加载到指定内存区域
	
	pop bp
	pop es
	pop ds
	pop ax
	ret  
_loadTest endp

public _jump
_jump proc
	push bp
	mov bp,sp
	
	push ax
	push bx
	push cx
	push dx
	push di
	push es
	push ds
	push si
	pushf

	mov bx,2000h				;段地址
	mov ax,100h					;偏移地址

	mov es,bx
	lea si,testbegin
	mov di,0
	lea cx,testend
	sub cx,si					;循环次数
	rep movsb					;循环写
	
	lea si,sp_place
	mov [si],sp
	
	mov ss,bx					;切换到用户栈
	mov sp,0
	
	xor cx,cx
	push cx						;压0x0000
	push bx						;要跳转的cs
	push ax						;要跳转的ip
	retf						;跳转
	
testret:
	popf						;恢复寄存器
	pop si
	pop ds
	pop es
	pop di
	pop dx
	pop cx
	pop bx
	pop ax
	pop bp
	ret

testbegin:
	int 20h						;用int 20h返回
testend:nop

_jump endp

; 时钟中断处理程序
Timer:
	call _save				; save保护中断现场
	mov ax,cs
	mov ds,ax
	lea bx,count			; 判断count值是否为0，为0显示下一个"风火轮"
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
	add bx,ax				; [bx]是要显示的字符，加上偏移量获取	
	mov ax,0b800h
	mov es,ax
	mov al,[bx]
	mov ah,0Fh				; 黑底白字
	mov bx,((24*80+79)*2)	; 24行79列
	mov es:[bx],ax
exit:
	mov al,20h				; AL = EOI
	out 20h,al				; 发送EOI到主8529A
	out 0A0h,al				; 发送EOI到从8529A
	jmp _restart			; restart恢复现场
	
	Delay equ 5
	count label byte
		db Delay
	wheel label byte
		db 1
		db '|'
		db '/'
		db '\'

; int20h 用户程序返回
int20h:	
	mov ax,cs
    mov ds,ax
    mov es,ax
    mov ss,ax
	lea si,sp_place
	mov sp,[si]
	jmp testret

; int21h 完成系统内核的调用       
int21h:
	cmp ah,0
	jz printChar
	cmp ah,1
	jnz next1
	jmp Readchar
next1:
	cmp ah,2
	jnz next2
	jmp clear
next2:
	cmp ah,3
	jnz next3
	jmp PowerOff
next3:
	cmp ah,4
	jnz quit
	jmp Reboot
quit:
	iret

printChar:
	push bp
	mov bp,sp
	mov al,[bp+10]
	mov bl,0
	mov ah,0eh
	int 10h
	mov sp,bp
	pop bp
	iret
Readchar:
	mov ah,0
    int 16h
	mov byte ptr [_x],al
	iret
clear:
	push ax
	push bx
	push cx
	push dx		
	mov	ax,600h		; AH = 6,  AL = 0
	mov	bx,700h		; 黑底白字(BL = 7)
	mov	cx,0		; 左上角: (0, 0)
	mov	dx,184fh	; 右下角: (24, 79)
	int	10h			; 显示中断

	mov ah,2
	mov bh,0
	mov dx,0
	int 10h

	pop dx
	pop cx
	pop bx
	pop ax
	iret
PowerOff:               
	mov ax,5307H 	; 高级电源管理功能,设置电源状态 
	mov bx,0001H 	; 设备ID1:所有设备 
	mov cx,0003H 	; 状态3:表示关机 
	int 15H 
Reboot:                   
    mov al, 0FEh
    out 64h, al
    iret
	
; int22h 输出“INT22H”      
public _int22h
_int22h proc 
	int 22h
	ret
_int22h endp

int22hprint:
	push ds
	push es
	push ax
	push bx
	push cx
	push si
	
	mov ah,13h 	    ; 功能号
	mov al,0    	; 光标返回起始位置
	mov bl,0Fh		; 0000：黑底、1111：亮白字
	mov bh,0 	                    	
	mov dh,15 		; 行
	mov dl,45 		; 列
	mov cx,6 	    ; 串长
	mov bp,offset int22hstr
	int 10h
	
	pop si
	pop cx
	pop bx
	pop ax
	pop es
	pop ds
	iret
int22hstr db "INT22H"
	
; save
public _save
_save proc 
	push ds
	push cs
	pop  ds
	push si
	
	lea si,_current
	pop word ptr [si+16];保存si
	pop word ptr [si+14];保存ds
	
	lea si,return_place
	pop word ptr [si]	;保存_save返回点
	
	lea si,_current
	pop word ptr [si+22];保存ip
	pop word ptr [si+24];保存cs
	pop word ptr [si+26];保存flags
	
	mov [si+18],ss
	mov [si+20],sp
	
	mov si,ds
	mov ss,si
	
	lea si,_current
	mov sp,si
	add sp,14
	
	push es
	push bp
	push di
	push dx
	push cx
	push bx
	push ax
	
	lea si,sp_place
	mov sp,[si]
	
	lea si,return_place
	mov ax,[si]
	jmp ax
_save endp

; restart
public _restart
_restart proc 
	lea si,sp_place
	mov [si],sp
	lea sp,_current
	pop ax
	pop bx
	pop cx
	pop dx
	pop di
	pop bp
	pop es
	
	lea si,ds_place
	pop word ptr [si]
	lea si,si_place
	pop word ptr [si]
	
	lea si,bx_place
	mov [si],bx			;保护bx，用它给ss赋值
	
	pop bx				;恢复栈
	mov ss,bx
	mov bx,sp
	mov sp,[bx]
	
	add bx,2
	
	push word ptr [bx+4];flags,cs,ip压栈
	push word ptr [bx+2]
	push word ptr [bx]
	
	push ax
	push word ptr [si]	;把bx压栈保存
	lea si,ds_place
	mov ax,[si]
	lea si,si_place
	mov bx,[si]
	mov ds,ax
	mov si,bx
	
	pop bx
	pop ax
	iret
_restart endp

datadef:
	return_place label byte
		dw 0
	si_place label byte
		dw 0
	sp_place label byte
		dw 0
	bx_place label byte
		dw 0
	ds_place label byte
		dw 0
	