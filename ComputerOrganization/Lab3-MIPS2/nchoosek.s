main:
	li	$a0,4
	li	$a1,0
	jal	nchoosek		# evaluate C(4,0); should be 1
	jal	printv0
	li	$a0,4
	li	$a1,1
	jal	nchoosek		# evaluate C(4,1); should be 4
	jal	printv0
	li	$a0,4
	li	$a1,2
	jal	nchoosek		# evaluate C(4,2); should be 6
	jal	printv0
	li	$a0,4
	li	$a1,3
	jal	nchoosek		# evaluate C(4,3); should be 4
	jal	printv0
	li	$a0,4
	li	$a1,4
	jal	nchoosek		# evaluate C(4,4); should be 1
	jal	printv0
	li	$a0,4
	li	$a1,5
	jal	nchoosek		# evaluate C(4,5); should be 0
	jal	printv0
	li	$v0,10
	syscall
	

nchoosek:	# you fill in the prologue
	addi	$sp,$sp,-16		# 在栈中压入四个字的空间
	sw	$ra,12($sp)		# 在栈中保存返回地址
	sw	$s2,8($sp)		# 保存$s2，用于保存C(n-1,k)
	sw	$s1,4($sp)		# 保存$s1，用于保存k
	sw	$s0,0($sp)		# 保存$s1，用于保存n-1
	beq	$a1,$0,return1		# 如果k=0，跳转到return1
	beq	$a0,$a1,return1		# 如果n=k，跳转到return1
	beq	$a0,$0,return0		# 如果n=0，跳转到return0
	blt	$a0,$a1,return0		# 如果n<k，跳转到return0
	
	addi	$a0,$a0,-1		# $a0中的数据改为n - 1
	move	$s0,$a0			# 将$a0中的数据(n-1)存入$s0
	move	$s1,$a1			# 将$a1中的数据(k)存入$s1
	jal	nchoosek		# $v0 = C(n-1,k)

	move	$s2,$v0			# 将$v0中的数据(C(n-1,k))存入$s2
	move	$a0,$s0			# 将$s0中的数据(n-1)存入$a0
	addi	$a1,$s1,-1		# 将$s1中的数据(k)减1存入$a1
	jal	nchoosek		# $v0 = C(n-1,k-1)
	
	add	$v0,$v0,$s2		# C(n,k) = C(n-1,k) + C(n-1,k-1)
	j	return			# 跳转到return
return0:
	move	$v0,$0			# $v0 = 0
	j	return			# 跳转到return
return1:
	addi	$v0,$0,1		# $v0 = 1
	j 	return			# 跳转到return
	
return:		# you fill in the epilog
	lw	$s0,0($sp)		# 恢复旧的$s0中数据
	lw	$s1,4($sp)		# 恢复旧的$s1中数据
	lw	$s2,8($sp)		# 恢复旧的$s2中数据
	lw	$ra,12($sp)		# 恢复旧的返回地址
	addi	$sp,$sp,16		# 恢复栈指针
	jr      $ra			# 函数返回

printv0:
	addi	$sp,$sp,-4
	sw	$ra,0($sp)
	move	$a0,$v0
	li	$v0,1
	syscall
	li	$a0,'\n'
	li	$v0,11
	syscall
	lw	$ra,0($sp)
	addi	$sp,$sp,4
	jr	$ra
