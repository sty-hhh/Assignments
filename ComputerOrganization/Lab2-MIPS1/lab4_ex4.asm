          .data
source:   .word   7, 8, 9, 10, 8, 1, 1, 1
          .text
main:   la      $a0,source	     	#��������a��ַ
        add     $s0,$zero,$zero		#$s0�����ܺ�
        add     $s1,$zero,$zero		#$s1�������
loop:   lw      $v1, 0($a0)		#��$a0�е�Ԫ��һ�δμ��ص�$v1��
	beq     $v1,$zero,finish	#���$v1�ж���0������ѭ��
	add     $s0,$s0,$v1		#�ܺ�$s0ÿ�μ���$v1
        addiu   $s1, $s1, 1   		#����$s1ÿ�μ���1
        addiu   $a0, $a0, 4      	#����$a0Ѱ����һ����ַ
        bne     $v1, $zero, loop 	#���û����0����ѭ��
finish:
	div     $s0,$s1			#���ܺ�$s0���Ը���$s1
	mflo    $a0			#�����ƽ��������$a0��
	li      $v0, 1  
        syscall
        li      $v0, 10     
        syscall
