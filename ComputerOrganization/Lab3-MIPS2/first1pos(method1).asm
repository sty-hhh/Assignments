main:
	lui	$a0,0x8000
	jal	first1pos
	jal	printv0
	lui	$a0,0x0001
	jal	first1pos
	jal	printv0
	li	$a0,1
	jal	first1pos
	jal	printv0
	add	$a0,$0,$0
	jal	first1pos
	jal	printv0
	li	$v0,10
	syscall

first1pos:	# your code goes here
	beq 	$a0,$0,false		# ���$a0=0����ת��false
	addi   	$s0,$0,31		# $s0��ֵ31
	addi   	$s1,$0,0x80000000	# $s1��ֵ0x80000000
loop:
	and	$t0,$a0,$s1		# ��$a0��$s1��λ��Ľ���ŵ�$t0
	bne 	$t0,$0,then 		# ���$t0!=0������ʱ$a0���λ��Ϊ0����ת��then
	sll	$a0,$a0,1		# ���$t0=0������ʱ$a0���λ��Ȼ��0����$a0����һλ
	addi 	$s0, $s0, -1		# $s0 = $s0 - 1 ������$a0����һλ
	j	loop			# ��ת��loop����������
then:    
	move    $v0, $s0		# $v0 = $s0�����Ϊ$a0��������ߵķ���λ��λ��
	jr 	$ra	                # ��������
false: 
	addi 	$v0,$0, -1		# $v0 = -1��δ�ҵ�������
	jr 	$ra			# ��������

printv0:
	addi	$sp,$sp,-4
	sw	$ra,0($sp)
	add	$a0,$v0,$0
	li	$v0,1
	syscall
	li	$v0,11
	li	$a0,'\n'
	syscall
	lw	$ra,0($sp)
	addi	$sp,$sp,4
	jr	$ra