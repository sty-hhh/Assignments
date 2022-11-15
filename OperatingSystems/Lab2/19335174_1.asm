 	Dn_Rt equ 1                  ;D-Down,U-Up,R-right,L-Left
    Up_Rt equ 2                  ;
    Up_Lt equ 3                  ;
    Dn_Lt equ 4                  ;
    delay equ 50000				 ; 计时器延迟计数,用于控制画框的速度
    ddelay equ 580				 ; 计时器延迟计数,用于控制画框的速度
	org 8100h

cls: ;清屏
    mov ah,6
    mov al,0
    mov ch,0  
    mov cl,0
    mov dh,24  
    mov dl,79
    mov bh,7 
    int 10h

start: 
    mov ax,cs					;获得程序运行时，代码段在内存的位置
	mov ds,ax					; DS = CS
	mov ss,ax					; SS = CS
	mov	ax,0B800h				; 文本窗口显存起始地址
	mov	es,ax					; ES = B800h

loop1:
	dec word[count]				; 递减计数变量
	jnz loop1					; >0：跳转;
	mov word[count],delay
	dec word[dcount]				; 递减计数变量
      jnz loop1
	mov word[count],delay
	mov word[dcount],ddelay

      mov al,1
      cmp al,byte[rdul]
	jz  DnRt
      mov al,2
      cmp al,byte[rdul]
	jz  UpRt
      mov al,3
      cmp al,byte[rdul]
	jz  UpLt
      mov al,4
      cmp al,byte[rdul]
	jz  DnLt
      jmp $	

DnRt:
	inc word[x]
	inc word[y]
	mov bx,word[x]
	mov ax,14
	sub ax,bx
      jz  dr2ur
	mov bx,word[y]
	mov ax,40
	sub ax,bx
      jz  dr2dl
	jmp show
dr2ur:
      mov word[x],12
      mov byte[rdul],Up_Rt	
      jmp show
dr2dl:
      mov word[y],38
      mov byte[rdul],Dn_Lt	
      jmp show
UpRt:
	dec word[x]
	inc word[y]
	mov bx,word[y]
	mov ax,40
	sub ax,bx
      jz  ur2ul
	mov bx,word[x]
	mov ax,-1
	sub ax,bx
      jz  ur2dr
	jmp show
ur2ul:
      mov word[y],38
      mov byte[rdul],Up_Lt	
      jmp show
ur2dr:
      mov word[x],1
      mov byte[rdul],Dn_Rt	
      jmp show	
UpLt:
	dec word[x]
	dec word[y]
	mov bx,word[x]
	mov ax,-1
	sub ax,bx
      jz  ul2dl
	mov bx,word[y]
	mov ax,-1
	sub ax,bx
      jz  ul2ur
	jmp show
ul2dl:
      mov word[x],1
      mov byte[rdul],Dn_Lt	
      jmp show
ul2ur:
      mov word[y],1
      mov byte[rdul],Up_Rt	
      jmp show	
DnLt:
	inc word[x]
	dec word[y]
	mov bx,word[y]
	mov ax,-1
	sub ax,bx
      jz  dl2dr
	mov bx,word[x]
	mov ax,14
	sub ax,bx
      jz  dl2ul
	jmp show
dl2dr:
      mov word[y],1
      mov byte[rdul],Dn_Rt	
      jmp show	
dl2ul:
      mov word[x],12
      mov byte[rdul],Up_Lt	
      jmp show
	
show:
	xor ax,ax
	mov word ax,[x]
	mov bx,80
	mul bx
	add word ax,[y]
	mov bx,2
	mul bx
	mov bx,ax
	mov si, NUMBER
	mov cx, 8
	color:
		mov byte al,[si]
		mov [es:bx],ax
		inc si
		inc bx
		inc bx
	loop color

    ; 输入空格后弹出程序
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
    rdul db Dn_Rt         ; 向右下运动
    x    dw -1
    y    dw 0
	NUMBER db "19335174"
	
	times 512-($-$$) db 0