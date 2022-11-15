          .data
source:   .word   7, 8, 9, 10, 8, 1, 1, 1
          .text
main:   la      $a0,source	     	#加载数组a地址
        add     $s0,$zero,$zero		#$s0代表总和
        add     $s1,$zero,$zero		#$s1代表个数
loop:   lw      $v1, 0($a0)		#将$a0中的元素一次次加载到$v1中
	beq     $v1,$zero,finish	#如果$v1中读到0则跳出循环
	add     $s0,$s0,$v1		#总和$s0每次加上$v1
        addiu   $s1, $s1, 1   		#个数$s1每次加上1
        addiu   $a0, $a0, 4      	#数组$a0寻找下一个地址
        bne     $v1, $zero, loop 	#如果没读到0继续循环
finish:
	div     $s0,$s1			#用总和$s0除以个数$s1
	mflo    $a0			#将结果平均数存入$a0中
	li      $v0, 1  
        syscall
        li      $v0, 10     
        syscall
