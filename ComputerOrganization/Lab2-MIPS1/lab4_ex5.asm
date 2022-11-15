          .data
source:   .word   7,8,9,10,8
maxint:   .word   999
          .text
main:   la      $a0,source                #加载数组a地址
	la      $s0,maxint                #$s0代表b
loop:   lw      $v1, 0($a0)		  #将$a0中的元素一次次加载到$v1中
	beq     $v1,$zero,finish	  #如果$v1中读到0则跳出循环
	slt     $t0,$v1,$s0		  #如果$v1小于$s0(b)则$t0=1
	beq     $t0,$zero,else		  #如果$t0=0则跳转到else
	add     $s0,$zero,$v1		  #如果$t0=1则将$v1的值赋给$s0(b)
else:	addiu   $a0, $a0, 4      	  #数组$a0寻找下一个地址
        bne     $v1, $zero, loop  	  #如果没读到0继续循环
finish:
	add     $a0,$zero,$s0		  #将最小数$s0(b)存入$a0中
	li      $v0, 1  
        syscall
        li      $v0, 10     
        syscall

	
	
