extern  macro %1    ;统一用extern导入外部标识符
	extrn %1
endm

extern _main:near

.8086
_TEXT segment byte public 'CODE'        
assume cs:_TEXT                         
DGROUP group _TEXT,_DATA,_BSS  
org 100h

start:	
	mov ax,cs
	mov ds,ax
	mov es,ax
	call near ptr _main
	
	ret
	include libs.asm
_TEXT ends

_DATA segment word public 'DATA'
_DATA ends

_BSS segment word public 'BSS'
_BSS ends

end start                            

