          .data
source:   .word   7,8,9,10,8
maxint:   .word   999
          .text
main:   la      $a0,source                #��������a��ַ
	la      $s0,maxint                #$s0����b
loop:   lw      $v1, 0($a0)		  #��$a0�е�Ԫ��һ�δμ��ص�$v1��
	beq     $v1,$zero,finish	  #���$v1�ж���0������ѭ��
	slt     $t0,$v1,$s0		  #���$v1С��$s0(b)��$t0=1
	beq     $t0,$zero,else		  #���$t0=0����ת��else
	add     $s0,$zero,$v1		  #���$t0=1��$v1��ֵ����$s0(b)
else:	addiu   $a0, $a0, 4      	  #����$a0Ѱ����һ����ַ
        bne     $v1, $zero, loop  	  #���û����0����ѭ��
finish:
	add     $a0,$zero,$s0		  #����С��$s0(b)����$a0��
	li      $v0, 1  
        syscall
        li      $v0, 10     
        syscall

	
	
