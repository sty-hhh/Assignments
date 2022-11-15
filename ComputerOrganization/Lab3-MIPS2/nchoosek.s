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
	addi	$sp,$sp,-16		# ��ջ��ѹ���ĸ��ֵĿռ�
	sw	$ra,12($sp)		# ��ջ�б��淵�ص�ַ
	sw	$s2,8($sp)		# ����$s2�����ڱ���C(n-1,k)
	sw	$s1,4($sp)		# ����$s1�����ڱ���k
	sw	$s0,0($sp)		# ����$s1�����ڱ���n-1
	beq	$a1,$0,return1		# ���k=0����ת��return1
	beq	$a0,$a1,return1		# ���n=k����ת��return1
	beq	$a0,$0,return0		# ���n=0����ת��return0
	blt	$a0,$a1,return0		# ���n<k����ת��return0
	
	addi	$a0,$a0,-1		# $a0�е����ݸ�Ϊn - 1
	move	$s0,$a0			# ��$a0�е�����(n-1)����$s0
	move	$s1,$a1			# ��$a1�е�����(k)����$s1
	jal	nchoosek		# $v0 = C(n-1,k)

	move	$s2,$v0			# ��$v0�е�����(C(n-1,k))����$s2
	move	$a0,$s0			# ��$s0�е�����(n-1)����$a0
	addi	$a1,$s1,-1		# ��$s1�е�����(k)��1����$a1
	jal	nchoosek		# $v0 = C(n-1,k-1)
	
	add	$v0,$v0,$s2		# C(n,k) = C(n-1,k) + C(n-1,k-1)
	j	return			# ��ת��return
return0:
	move	$v0,$0			# $v0 = 0
	j	return			# ��ת��return
return1:
	addi	$v0,$0,1		# $v0 = 1
	j 	return			# ��ת��return
	
return:		# you fill in the epilog
	lw	$s0,0($sp)		# �ָ��ɵ�$s0������
	lw	$s1,4($sp)		# �ָ��ɵ�$s1������
	lw	$s2,8($sp)		# �ָ��ɵ�$s2������
	lw	$ra,12($sp)		# �ָ��ɵķ��ص�ַ
	addi	$sp,$sp,16		# �ָ�ջָ��
	jr      $ra			# ��������

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
