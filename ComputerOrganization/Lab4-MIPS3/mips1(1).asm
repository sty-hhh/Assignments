     	.data
K:   	.word   0
Y:  	.word   56
Z:	.space 	200		# 给数组Z分配50*4=200个字节的空间
str: 	.asciiz "  "
        .text
main:
	lw	$s1,K		# $s1代表K
	lw	$s2,Y		# $s2代表Y
	la 	$s3,Z		# $s3代表数组Z
loop:
	slti 	$t0,$s1,50	# 若K<50，$t0 = 1，否则$t0 = 0
	beq 	$t0,$0,exit	# 若$t0 = 0，即K>=50，则跳转到exit（跳出循环）
	srl 	$t1,$s1,2	# 将$s1右移两位，即$t1 = K / 4
	addi	$t1,$t1,210	# $t1 = $t1 + 210
	sll	$t1,$t1,4	# 将$t1左移4位，即$t1 = $t1 * 16
	sub	$t1,$s2,$t1	# $t1 = $s2(Y) - $t1
	sw	$t1,0($s3)	# 将$t1的值存入$s3(数组Z)的相应位置中
	lw	$a0,0($s3)	# 输出数组Z当前位置的值
	li	$v0,1
	syscall
	la 	$a0,str		# 输出空格“ ”
	li	$v0,4
	syscall
	addi	$s3,$s3,4	# 让数组Z寻址到下一个位置（4个字节）
	addi	$s1,$s1,1	# K = K + 1
	j	loop		# 跳转到loop，继续循环
exit:
	li	$v0,10		# 程序终止结束
	syscall
