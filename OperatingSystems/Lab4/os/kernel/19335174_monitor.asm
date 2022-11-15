extern  macro %1    ;统一用extern导入外部标识符
	extrn %1
endm

extern _cmain:near


;*****************************************
.8086                                   ;*
_TEXT segment byte public 'CODE'        ;*
assume cs:_TEXT                         ;*
DGROUP group _TEXT,_DATA,_BSS           ;* 
org 100h                                ;*
                                        ;*
start:                                  ;*
;*****************************************
;
	xor ax, ax
	mov es, ax
	mov word ptr es:[20h],offset Timer
	mov word ptr es:[22h],cs
	
	mov ax,cs
	mov ds,ax; DS = CS
	mov es,ax; ES = CS
	mov ss,ax; SS = cs
	mov sp,0FFF0h   
	mov ah,2
	mov bh,0
	mov dx,0
	int 10h
	
	call near ptr _cmain
    jmp $	
	
	include kliba.asm
;
;*****************************************
                                        ;*
_TEXT ends                              ;*
                                        ;*
_DATA segment word public 'DATA'        ;*
                                        ;*
_DATA ends                              ;*
                                        ;*
_BSS	segment word public 'BSS'       ;*
_BSS ends                               ;*
                                        ;* 
end start                               ;*
;*****************************************
