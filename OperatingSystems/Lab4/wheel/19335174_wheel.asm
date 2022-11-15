	org 100h			; 程序加载到100h，可用于生成COM
; 设置时钟中断向量（08h），初始化段寄存器
	xor ax,ax			; AX = 0
	mov es,ax			; ES = 0
	mov word [es:20h],Timer	; 设置时钟中断向量的偏移地址
	mov ax,cs 
	mov word [es:22h],ax		; 设置时钟中断向量的段地址=CS
	mov ds,ax			; DS = CS
	mov es,ax			; ES = CS

	mov	ax,0B800h		; 文本窗口显存起始地址
	mov	gs,ax		; GS = B800h
	mov ah,0Fh		; 0000：黑底、1111：亮白字（默认值为07h）
	jmp $			; 死循环
; 时钟中断处理程序	
Timer:
	dec byte [count]	 ;递减计数变量
	jnz end				 ;非0则跳转返回，5次中断和中断返回做一次切换
	mov byte[count],delay;BS恢复计数变量

	mov si,wheel		 
	add si,[offset]
	mov al,byte [si]			
	mov [gs:((80*24+79)*2)],ax		;打印

	add byte[offset],1    
	cmp byte[offset],3  
	jne end                 
	mov byte[offset],0  

end:
	mov al,20h			; AL = EOI
	out 20h,al			; 发送EOI到主8529A
	out 0A0h,al			; 发送EOI到从8529A
	iret			;从中断返回

datadef:
	delay equ 5		
	count db delay		
	wheel db '|/\'          
	offset db 0