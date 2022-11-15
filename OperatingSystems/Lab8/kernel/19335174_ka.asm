;BIOS基础系统调用

; 导入全局变量
extern _x
extern _curPCB
extern _kerPCB
extern _ttime
extern _ddate
extern _schedule
extern _endProcess
extrn _do_fork
extrn _do_exit
extrn _do_wait
extrn _do_GetSema
extrn _do_FreeSema
extrn _do_P
extrn _do_V

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
	mov ah,0h
	int 21h
	ret
_printChar endp

; 读取一个字符
public _getChar
_getChar proc
	mov ah,1h
    int 21h
	mov byte ptr [_x],al
	ret
_getChar endp

; 清屏
public _cls
_cls proc 
	mov ah,2h
	int 21h
	ret
_cls endp

; 关机                
public _PowerOff
_PowerOff proc                  
	mov ah,3h
	int 21h
	ret
_PowerOff endp

;重启
public _Reboot
_Reboot proc                     
    mov ah,4h
	int 21h
	ret
_Reboot endp

public _fork
_fork proc 
	push bp
	mov bp,sp
	push bx
	mov bx,[bp+4]
	mov ah,5h
	int 21h
	pop bx
	pop bp
	ret
_fork endp

public _exit
_exit proc 
	mov ah,6h
	int 21h
	ret
_exit endp

public _wait
_wait proc 
	mov ah,7h
	int 21h
	ret
_wait endp

public _GetSema
_GetSema proc 
	push bp
	mov bp,sp
	push bx
	mov bx,[bp+4]
	mov ah,8h
	int 21h
	pop bx
	pop bp
	ret
_GetSema endp

public _FreeSema
_FreeSema proc 
	push bp
	mov bp,sp
	push bx
	mov bx,[bp+4]
	mov ah,9h
	int 21h
	pop bx
	pop bp
	ret
_FreeSema endp

public _P
_P proc 
	push bp
	mov bp,sp
	push bx
	mov bx,[bp+4]
	mov ah,0Ah
	int 21h
	pop bx
	pop bp
	ret
_P endp

public _V
_V proc 
	push bp
	mov bp,sp
	push bx
	mov bx,[bp+4]
	mov ah,0Bh
	int 21h
	pop bx
	pop bp
	ret
_V endp

; 加载用户程序5个参数(cs段地址，ip偏移地址，head磁头号，id起始扇区号，num扇区数)
public _loadProgram
_loadProgram proc
	push bp
	mov bp,sp

	push ax
	push bx
	push cx
	push dx
	push es
	
	mov ax,[bp+4]			; 段地址，存放数据的内存基地址
	mov es,ax               ; 设置段地址（不能直接mov es,段地址）
	mov bx,[bp+6]			; 偏移地址; 存放数据的内存偏移地址
	mov ah,2                ; 功能号2
	mov al,[bp+12]          ; 扇区数
	mov dl,0                ; 驱动器号 ; 软盘为0，硬盘和U盘为80H
	mov dh,[bp+8]           ; 磁头号，起始编号为0
	mov ch,0                ; 柱面号，起始编号为0
	mov cl,[bp+10]          ; 起始扇区号 ; 起始编号为1
	int 13H                 ; 调用读磁盘BIOS的13h功能
	;用户程序已加载到指定内存区域
	
	pop es
	pop dx
	pop cx
	pop bx
	pop ax
	pop bp
	ret  
_loadProgram endp

; 加载代码段前缀到指定的段
public _loadReady
_loadReady proc
	push bp
	mov bp,sp
	
	push cx
	push es
	push si
	push di

	mov ax,[bp+4]
	mov es,ax				; 段地址
	xor di,di
	mov ax,cs
	mov ds,ax
	lea si,testbegin
	lea cx,testend
	sub cx,si				; 循环次数
	rep movsb				; 循环写
	
	pop di
	pop si
	pop es
	pop cx
	pop bp
	ret 
	
testbegin:
	int 20h					; 用int 20h返回
testend:nop
_loadReady endp

; 开中断
public _setIF
_setIF proc near
	sti
_setIF endp

; 初始化用户进程的栈
public _InitStack
_InitStack proc 
	push bp
	mov bp,sp
	push bx
	mov bx,1000h			;所有用户程序的栈段都在这里
	mov ss,bx
	mov ax,[bp+4]
	mov sp,ax
	xor ax,ax
	push ax					;用户栈里压一个0000
	mov ax,sp				
	mov bx,cs
	mov ss,bx
	sub bp,2				;ss:bp==bx
	mov sp,bp
	pop bx
	pop bp
	ret
_InitStack endp

; 时钟中断处理程序
Timer:
	call _save				; save保护中断现场
	
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
	push es	
	mov ax,0b800h
	mov es,ax
	mov al,[bx]
	mov ah,0Fh				; 黑底白字
	mov bx,((24*80+79)*2)	; 24行79列
	mov es:[bx],ax
	pop es
exit:
	call _date				; 显示日期
	call _time				; 显示时间
	call near ptr _schedule	; 进程调度
	
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

public _time
_time proc
	push ds
    push es
	
    mov ax,cs
	mov ds,ax           	; DS = CS
	mov ax,cs
	mov es,ax           	; ES = CS
	mov di,offset _ttime
	
	mov ah,02h				; 读取时钟
    int 1Ah
    mov al,ch
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [di],al
	
    mov ah,02h
    int 1Ah
    mov al,ch
	and al,0fh
	add al,30h
	mov [di+1],al	
    mov byte ptr [di+2],':'	
	
	mov ah,02h				; 读取分钟
    int 1Ah
    mov al,cl
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [di+3],al
	
    mov ah,02h
    int 1Ah
    mov al,cl
    and al,0fh
    add al,30h
	mov [di+4],al
	mov byte ptr [di+5],':'	

	mov ah,02h				; 读取秒钟
    int 1Ah
    mov al,dh
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [di+6],al
	
    mov ah,02h
    int 1Ah
    mov al,dh
    and al,0fh
    add al,30h
	mov [di+7],al
	mov byte ptr [di+8],' '	
	
	mov ax,cs
	mov ds,ax           	; DS = CS
	mov es,ax           	; ES = CS
	mov	bp,offset _ttime 	; BP=当前串的偏移地址
	mov	ax,ds			    ; ES:BP = 串地址
	mov	es,ax			    ; 置ES=DS 
	mov	cx,9         		; CX = 串长（=9）
	mov	ax,1300h	 		; AH = 13h（功能号）、AL = 00h（光标置于起始位置）
	mov	bx,0007h			; 页号为0(BH = 0) 黑底白字(BL = 07h)			
	mov dh,24				; 行号=24
	mov	dl,70				; 列号=70
	int	10h					; BIOS的10h功能：显示一行字符

    pop es
    pop ds
	ret
_time endp

public _date
_date proc
	push ds
    push es
	
    mov ax,cs
	mov ds,ax				; DS = CS
    mov ax,cs
	mov es,ax       		; ES = CS
	mov si,offset _ddate

	mov ah,04h				; 读取世纪
    int 1Ah
    mov al,ch
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [si],al

    mov ah,04h				
    int 1Ah
    mov al,ch
    and al,0fh
    add al,30h
	mov [si+1],al
	
	mov ah,04h				; 读取年份
    int 1Ah
    mov al,cl
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [si+2],al

    mov ah,04h
    int 1Ah
    mov al,cl
    and al,0fh
    add al,30h
	mov [si+3],al
    mov byte ptr [si+4],'.'

	mov ah,04h				; 读取月份
    int 1Ah
    mov al,dh
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [si+5],al

    mov ah,04h
    int 1Ah
    mov al,dh
    and al,0fh
	add al,30h
	mov [si+6],al
	mov byte ptr [si+7],'.'

	mov ah,04h				; 读取天数
    int 1Ah
    mov al,dl
	mov ah,0
	mov bl,16
	div bl
	add al,30h
	mov [si+8],al

    mov ah,04h
    int 1Ah
    mov al,dl
    and al,0fh
	add al,30h
	mov [si+9],al
	mov byte ptr [si+10],' '
	
	mov ax,cs
	mov ds,ax           	; DS = CS
	mov es,ax           	; ES = CS
	mov	bp,offset _ddate 	; BP=当前串的偏移地址
	mov	ax,ds			    ; ES:BP = 串地址
	mov	es,ax			    ; 置ES=DS 
	mov	cx,11         		; CX = 串长（=11）
	mov	ax,1300h	 		; AH = 13h（功能号）、AL = 00h（光标置于起始位置）
	mov	bx,0007h			; 页号为0(BH = 0) 黑底白字(BL = 07h)			
	mov dh,24				; 行号=24
	mov	dl,59				; 列号=59
	int	10h					; BIOS的10h功能：显示一行字符

    pop es
    pop ds
	ret
_date endp

; int20h 用户程序返回
int20h:	
	mov ax,cs
    mov ds,ax
    mov es,ax
    mov ss,ax
	mov si,word ptr [_kerPCB]	; 保存到内核PCB
	mov sp,[si+20]
	jmp near ptr _endProcess	; 结束进程

; int21h 完成系统内核的调用       
int21h:
	cmp ah,0h
	jz printChar
	cmp ah,1h
	jnz next1
	jmp Readchar
next1:
	cmp ah,2h
	jnz next2
	jmp clear
next2:
	cmp ah,3h
	jnz next3
	jmp PowerOff
next3:
	cmp ah,4h
	jnz next4
	jmp Reboot
next4:
	cmp ah,5h
	jnz next5
	jmp fork0
next5:
	cmp ah,6h
	jnz next6
	jmp exit0
next6:
	cmp ah,7h
	jnz next7
	jmp wait0
next7:
	cmp ah,8h
	jnz next8
	jmp do_GetSema0
next8:
	cmp ah,9h
	jnz next8
	jmp do_FreeSema0
next9:
	cmp ah,0Ah
	jnz next10
	jmp do_P0
next10:
	cmp ah,0Bh
	jnz quit
	jmp do_V0
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
fork0:
	call _save
	call near ptr _do_fork
	jmp _restart
exit0:
	call _save
	call near ptr _do_exit
	jmp _restart
wait0:
	call _save
	call near ptr _do_wait
	jmp _restart
do_GetSema0:
	call _save
	call _do_GetSema
	jmp _restart
do_FreeSema0:
	call _save
	call _do_FreeSema
	jmp _restart
do_P0:
	call _save
	call _do_P
	jmp _restart
do_V0:
	call _save
	call _do_V
	jmp _restart

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

public _save
_save proc 
	push ds
	push cs
	pop ds						
	push si
	
	mov si,word ptr [_curPCB]	; 保存_curPCB的内容
	pop word ptr [si+16]		; 保存si
	pop word ptr [si+14]		; 保存ds
	
	lea si,ret_save				; 保存_save的返回点
	pop word ptr [si]			
	
	mov si,word ptr [_curPCB]
	pop word ptr [si+22]		; 保存ip
	pop word ptr [si+24]		; 保存cs
	pop word ptr [si+26]		; 保存flags
	
	mov [si+18],ss
	mov [si+20],sp
	
	mov si,ds
	mov ss,si
	
	mov sp,word ptr [_curPCB]
	add sp,14
	
	push es
	push bp
	push di
	push dx
	push cx
	push bx
	push ax
	
	mov si,word ptr [_kerPCB]
	mov sp,[si+20]
	mov ax,cs
	mov es,ax
	
	lea si,ret_save
	mov ax,[si]
	jmp ax
_save endp

public _restart
_restart proc 
	mov si,word ptr [_kerPCB]
	mov [si+20],sp
	mov sp,word ptr [_curPCB]
	pop ax
	pop bx
	pop cx
	pop dx
	pop di
	pop bp
	pop es						
	
	lea si,ds_save
	pop word ptr [si]
	lea si,si_save
	pop word ptr [si]
	
	lea si,bx_save
	mov [si],bx					; 保护bx，用它给ss赋值
	
	pop bx						; 恢复栈
	mov ss,bx
	mov bx,sp
	mov sp,[bx]
	
	add bx,2
	push word ptr [bx+4]		; flags,cs,ip压栈
	push word ptr [bx+2]
	push word ptr [bx]
	
	push ax
	push word ptr [si]			; 把bx压栈保存
	lea si,ds_save
	mov ax,[si]
	lea si,si_save
	mov bx,[si]
	mov ds,ax
	mov si,bx
	
	pop bx
	pop ax
	iret
_restart endp

datadef:
	si_save dw ?
	ds_save dw ?
	bx_save dw ?
	ret_save dw ?
	kernelsp dw ?
	
	
