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
	ori $sp,$sp,0x2ffc	#ջ��ʼ��
	addiu $sp,$sp,-16	#��ջ��ѹ���ĸ��ֵĿռ�
	lw $24,($4) 		#��$a0����(n1)�ŵ�$t8��
	sw $24,12($sp) 		#��$t8���ݴ���ջ��
	lw $24,0($5) 		#��$a1����(n2)�ŵ�$t8��
	sw $24,0($4) 		#��$t8����(n2)�浽$a0��
	lw $24,12($sp) 		#��ջ�е�����(n1)�ŵ�$t8��
	sw $24,($5) 		#��$t8����(n1)�浽$a1��
L_1:  	addiu $sp,$sp,16 	#�ָ�ջָ��
       	jr $31 			#��������

	.data
n1:	.word	14
n2:	.word	27
