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
	beq 	$a0,$0,false		# 如果$a0=0，跳转到false
	addi   	$s0,$0,31		# $s0赋值31
	addi   	$s1,$0,0x80000000	# $s1赋值0x80000000
loop:
	and	$t0,$a0,$s1		# 将$a0和$s1按位与的结果放到$t0
	bne 	$t0,$0,then 		# 如果$t0!=0，即此时$a0最高位不为0，跳转到then
	sll	$a0,$a0,1		# 如果$t0=0，即此时$a0最高位依然是0，将$a0左移一位
	addi 	$s0, $s0, -1		# $s0 = $s0 - 1 计算检测$a0的哪一位
	j	loop			# 跳转到loop，继续查找
then:    
	move    $v0, $s0		# $v0 = $s0，结果为$a0字中最左边的非零位的位置
	jr 	$ra	                # 函数返回
false: 
	addi 	$v0,$0, -1		# $v0 = -1，未找到非零数
	jr 	$ra			# 函数返回

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