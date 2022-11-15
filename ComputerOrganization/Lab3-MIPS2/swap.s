.text
main:
	la	$a0,n1
	la	$a1,n2
	jal	swap
	li	$v0,1	# print n1 and n2; should be 27 and 14
	lw	$a0,n1
	syscall
	li	$v0,11
	li	$a0,' '
	syscall
	li	$v0,1
	lw	$a0,n2
	syscall
	li	$v0,11
	li	$a0,'\n'
	syscall
	li	$v0,10	# exit
	syscall

swap:	
	ori $sp,$sp,0x2ffc	#栈初始化
	addiu $sp,$sp,-16	#在栈中压入四个字的空间
	lw $24,($4) 		#将$a0数据(n1)放到$t8中
	sw $24,12($sp) 		#将$t8数据存入栈中
	lw $24,0($5) 		#将$a1数据(n2)放到$t8中
	sw $24,0($4) 		#将$t8数据(n2)存到$a0中
	lw $24,12($sp) 		#将栈中的数据(n1)放到$t8中
	sw $24,($5) 		#将$t8数据(n1)存到$a1中
L_1:  	addiu $sp,$sp,16 	#恢复栈指针
       	jr $31 			#函数返回

	.data
n1:	.word	14
n2:	.word	27
