    D equ 1                  ;D-Down,U-Up,R-right,L-Left
    R equ 2                  ;
    U equ 3                  ;
    L equ 4                  ;
    delay equ 50000			 ; 计时器延迟计数,用于控制画框的速度
    ddelay equ 580			 ; 计时器延迟计数,用于控制画框的速度
	org 8100h
	
cls:	;清屏
    mov ah,6
    mov al,0
    mov ch,0  
    mov cl,0
    mov dh,24  
    mov dl,79
    mov bh,7 
    int 10h

showMessage:
    mov ax,Message
    mov bp,ax 	; es:bp串地址
    mov cx,11	; 字符串长度
    mov	ax, 1301h	 ; AH = 13h（功能号）、AL = 01h（光标置于串尾）
	mov	bx, 0007h	 ; 页号为0(BH = 0) 黑底白字(BL = 07h)
    mov dh, 05h		 ; 行号=0
	mov	dl, 37h		 ; 列号=0
	int	10h		 ; BIOS的10h功能：显示一行字符

start: 
    mov ax,cs					;获得程序运行时，代码段在内存的位置
	mov ds,ax					; DS = CS
	mov ss,ax					; SS = CS
	mov	ax,0B800h				; 文本窗口显存起始地址
	mov	es,ax					; ES = B800h

loop1:
	dec word[count]	
	jnz loop1				
	mov word[count],delay
	dec word[dcount]				; 递减计数变量
    jnz loop1
	mov word[count],delay
	mov word[dcount],ddelay 

    mov al,1
      cmp al,byte[rdul]
	jz  Down
      mov al,2
      cmp al,byte[rdul]
	jz  Right
      mov al,3
      cmp al,byte[rdul]
	jz  Up
      mov al,4
      cmp al,byte[rdul]
	jz  Left
      jmp $	
	
Down:
	inc word[x]
	mov bx,word[x]
	mov ax,12
	sub ax,bx
      jz  d2r
	jmp show
d2r:
    mov word[x],11
    mov byte[rdul],R	
    jmp show

Right:
	inc word[y]
	mov bx,word[y]
	mov ax,80
	sub ax,bx
      jz  r2u
	jmp show
r2u:
    mov word[y],79
    mov byte[rdul],U	
    jmp show
	
Up:
	dec word[x]
	mov bx,word[x]
	mov ax,-1
	sub ax,bx
      jz  u2l
	jmp show
u2l:
    mov word[x],0
    mov byte[rdul],L	
    jmp show

Left:
	dec word[y]
	mov bx,word[y]
	mov ax,39
	sub ax,bx
      jz  l2d
	jmp show
l2d:
    mov word[y],40
    mov byte[rdul],D	
    jmp show

show:	
    xor ax,ax                 ; 计算显存地址
    mov ax,word[x]
	mov bx,80
	mul bx
	add ax,word[y]
	mov bx,2
	mul bx
	mov bp,ax
	mov ah,0Fh				;  0000：黑底、1111：亮白字（默认值为07h）
	mov al,byte[char]			;  AL = 显示字符值（默认值为20h=空格符）
	mov word[es:bp],ax  		;  NASM汇编，显示字符的ASCII码值
	
	;输入空格弹出程序
    mov ah,1
    int 16h
    mov bl,20h
    cmp al,bl
    jz Quit
    jmp loop1

Quit:
    jmp 7c00h
end:
    jmp $                   ; 停止画框，无限循环 

datadef:	
    count dw delay 
    dcount dw ddelay
    rdul db D

    Message: db "19335174STY"
    x dw 0
    y dw 40
    char db 'A'
	
	times 512-($-$$) db 0