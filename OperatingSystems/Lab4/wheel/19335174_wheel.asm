	org 100h			; ������ص�100h������������COM
; ����ʱ���ж�������08h������ʼ���μĴ���
	xor ax,ax			; AX = 0
	mov es,ax			; ES = 0
	mov word [es:20h],Timer	; ����ʱ���ж�������ƫ�Ƶ�ַ
	mov ax,cs 
	mov word [es:22h],ax		; ����ʱ���ж������Ķε�ַ=CS
	mov ds,ax			; DS = CS
	mov es,ax			; ES = CS

	mov	ax,0B800h		; �ı������Դ���ʼ��ַ
	mov	gs,ax		; GS = B800h
	mov ah,0Fh		; 0000���ڵס�1111�������֣�Ĭ��ֵΪ07h��
	jmp $			; ��ѭ��
; ʱ���жϴ������	
Timer:
	dec byte [count]	 ;�ݼ���������
	jnz end				 ;��0����ת���أ�5���жϺ��жϷ�����һ���л�
	mov byte[count],delay;BS�ָ���������

	mov si,wheel		 
	add si,[offset]
	mov al,byte [si]			
	mov [gs:((80*24+79)*2)],ax		;��ӡ

	add byte[offset],1    
	cmp byte[offset],3  
	jne end                 
	mov byte[offset],0  

end:
	mov al,20h			; AL = EOI
	out 20h,al			; ����EOI����8529A
	out 0A0h,al			; ����EOI����8529A
	iret			;���жϷ���

datadef:
	delay equ 5		
	count db delay		
	wheel db '|/\'          
	offset db 0