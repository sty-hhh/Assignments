; 导入全局变量
extern _x
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
public _putch
_putch proc 
	mov ah,0h
	int 21h
	ret
_putch endp

; 读取一个字符
public _readch
_readch proc
	mov ah,1h
    int 21h
	mov byte ptr [_x],al
	ret
_readch endp

public _fork
_fork proc 
	mov ah,5h
	int 21h
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
