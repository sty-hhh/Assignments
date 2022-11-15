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
