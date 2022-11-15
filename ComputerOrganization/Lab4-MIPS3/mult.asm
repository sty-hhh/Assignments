     	.data
X:   	.word   -1073741824
Y:  	.word   1073741824
        .text
main:
	lw	$a0,X			# $a0代表被乘数的低32位
	lw	$a1,Y			# $a1代表乘数
	addi	$a2,$0,0		# $a2代表被乘数的高32位
	addi 	$v0,$0,0		# $v0代表积的高32位
	addi   	$v1,$0,0		# $v1代表积的低32位
	addi	$s0,$0,32		# $s0代表循环次数
		
	andi	$t0,$a0,0x80000000	# 如果被乘数最高位是1，说明它是负数，$t0 = 1
	andi 	$t1,$a1,0x80000000	# 如果乘数最高位是1，说明它是负数，$t1 = 1
	xor	$t2,$t0,$t1		# 如果被乘数和乘数符号相异，那么积是负数，$t2 = 1
j1:	bne	$t0,$0,neg1		# 如果被乘数是负数，跳转到neg1，取它的补码
j2: 	bne	$t1,$0,neg2		# 如果乘数是负数，跳转到neg2，取它的补码
	j 	loop			# 跳转到loop，开始计算乘积
	
neg1:	xori	$a0,$a0,0xFFFFFFFF	# 将被乘数取反
	addi	$a0,$a0,1		# 得到被乘数的补码
	j 	j2			# 跳转到j2，继续判断乘数是否是负数
neg2:	xori	$a1,$a1,0xFFFFFFFF	# 将乘数取反
	addi	$a1,$a1,1		# 得到乘数的补码
	j	loop			# 跳转到loop，开始计算乘积
			
loop:
	andi	$t0,$a1,1		# 如果乘数最低位是1，$t0 = 1
	beq	$t0,$0,then		# 乘数最低位是0，跳转到then
					# 乘数最低位是1，那么...		
	addu 	$v1,$a0,$v1		# 积的低32位 = 被乘数低32位 + 积的低32位
	sltu 	$t0,$v1,$a0		# 如果积的低32位 < 被乘数低32位，说明发生进位，要向高位进1
	addu 	$v0,$v0,$t0		# 积的高32位 = 积的高32位 + 进位
	addu 	$v0,$v0,$a2		# 积的高32位 = 积的高32位 + 被乘数的高32位	
then:	
	srl  	$a1,$a1,1		# 乘数右移一位
	sll	$a2,$a2,1		# 被乘数高32位左移一位
	andi	$t0,$a0,0x80000000	# 如果被乘数低32位的最高位是1，$t0 = 1
	sll	$a0,$a0,1		# 被乘数低32位左移一位
	beq	$t0,$0,L		# 如果被乘数低32位的最高位是0，即$t0 = 0,跳转到L
	ori	$a2,$a2,1		# 如果被乘数低32位的最高位是1，被乘数高32位的最低位 置1
L:	
	addi	$s0,$s0,-1		# 循环次数减1
	beq	$s0,$0,final		# 如果循环32次，跳转到final
	j	loop			# 未循环32次，跳转到loop，继续循环
	
final:
	bne	$t2,$0,neg3		# 如果最后结果是负的，跳转到neg3求整个积的补码
print:	
	addu	$a0,$v0,$0		# 输出积的高32位
	li	$v0,35			# 输出二进制
	syscall
	addu	$a0,$v1,$0		# 输出积的低32位
	li	$v0,35			# 输出二进制
	syscall
	li	$v0,10			# 程序结束
	syscall
	
neg3:	xori	$v0,$v0,0xFFFFFFFF	# 将积的高32位取反
	xori	$v1,$v1,0xFFFFFFFF	# 将积的低32位取反
	beq	$v1,0xFFFFFFFF,P	# 如果积的低32位是0xFFFFFFFF,加1会溢出，所以跳转到P进行防溢出操作
	addi	$v1,$v1,1		# 积的低32位加1（取补码）
	j 	print			# 跳转到print
P:	addi	$v1,$0,0		# 积的低32位清零
	addi	$v0,$v0,1		# 积的高32位加1
	j 	print			# 跳转到print
	
	
	
