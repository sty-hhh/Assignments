	.data
arr1: 	.word  	1:101
arr2:   .word   1:101
arr3:   .word   1:101
space:	.asciiz	" "
line:   .asciiz "\n"
	.text
	
	addi	$t0,$t0,7		# 输入的尺寸为7*7
	addi	$t1,$t1,3		# 卷积核的尺寸为3*3 
	move    $s0,$0			# 初始化
     	move    $s1,$0
     	move    $s2,$0 
read1:	mult    $s0,$t0			# 行号$s0 * 7
     	mflo    $s2			# $s2 = $s0 * 7
    	add    	$s2,$s2,$s1		# $s2 = $s2 + $s1，代表数组偏移量
     	li    	$v0,5			# 输入一个元素
     	syscall
     	move    $t4,$v0			# 将输入的元素放入数组$t4
     	sll    	$s2,$s2,2		# 因为一个输入4个字节，$s2*4是正确的偏移量
    	sw    	$t4,arr1($s2)    	# 将$t4的值存到arr1相应位置中
     	addi    $s1,$s1,1
     	bne    	$s1,$t0,read1		# 如果列号$s1小于7，继续循环
     	move    $s1,$0			# 如果列号$s1等于7，清零
     	addi    $s0,$s0,1		# 行号$s0加1
     	bne    	$s0,$t0,read1		# 如果行号$s0小于7，继续循环
     
     	move    $s0,$0			# 初始化
     	move    $s1,$0
     	move    $s2,$0
read2:	mult    $s0,$t1			# 行号$s0 * 3
     	mflo    $s2			# $s2 = $s0 * 3
     	add    	$s2,$s2,$s1		# $s2 = $s2 + $s1，代表数组偏移量
     	li    	$v0,5			# 输入一个元素
     	syscall
     	move    $t4,$v0			# 将输入的元素放入数组$t4
     	sll    	$s2,$s2,2		# 因为一个输入4个字节，$s2*4是正确的偏移量
    	sw    	$t4,arr2($s2)    	# 将$t4的值存到arr2相应位置中
    	addi    $s1,$s1,1		
     	bne    	$s1,$t1,read2		# 如果列号$s1小于3，继续循环
     	move    $s1,$0			# 如果列号$s1等于3，清零
     	addi    $s0,$s0,1		# 行号$s0加1
    	bne    	$s0,$t1,read2		# 如果行号$s0小于3，继续循环
    
     	sub    	$t2,$t0,$t1		
    	addi    $t2,$t2,1    		# 卷积计算结果$t2 = 7 - 3 + 1 = 5
     
     	move    $s0,$0    		# $s0 = i (循环变量)
for1:   move 	$s1,$0			# $s1 = j (循环变量)
for2:   move 	$s2,$0			# $s2 = k (循环变量)
	move	$t6,$0			# $t6清零，用于每次arr3的赋值
for3:	move 	$s3,$0			# $s3 = l (循环变量)
for4:	mul	$t3,$s0,$t2		
	add	$t3,$t3,$s1
	sll	$t3,$t3,2		# $t3 = i*5+j arr3的偏移量
	add	$t4,$s0,$s2
	mul	$t4,$t4,$t0
	add	$t4,$t4,$s1
	add	$t4,$t4,$s3
	sll	$t4,$t4,2		# $t4 = (i+k)*7+j+l arr1的偏移量
	mul	$t5,$s2,$t1
	add	$t5,$t5,$s3
	sll	$t5,$t5,2		# $t5 = k*3+l arr2的偏移量
	lw	$t7,arr1($t4)		# $t7为arr1对应值
	lw	$t8,arr2($t5)		# $t8为arr2对应值
	mul	$t9,$t7,$t8		# $t9 = $t7 * $t8 临时变量
	add	$t6,$t6,$t9		# $t6 = $t6 + $t9 arr3对应值
	sw	$t6,arr3($t3)		# 将$t6的值存入arr3对应位置
	addi	$s3,$s3,1		# l = l + 1
	bne	$s3,$t1,for4		# 如果l == 3，跳出循环
	addi	$s2,$s2,1		# k = k + 1
	bne	$s2,$t1,for3		# 如果k == 3，跳出循环
	addi	$s1,$s1,1		# j = j + 1
	bne	$s1,$t2,for2		# 如果j == 5，跳出循环
	addi	$s0,$s0,1		# i = i + 1
	bne	$s0,$t2,for1		# 如果i == 5，跳出循环
	
	move    $s0,$0 			# $s0 = i (循环变量)
print1:	move 	$s1,$0			# $s1 = j (循环变量)
print2:	mul	$t3,$s0,$t2	
	add	$t3,$t3,$s1
	sll	$t3,$t3,2		# $t3 = i*5+j arr3的偏移量
	lw	$a0,arr3($t3)
	li    	$v0,1
        syscall				# 输出arr3对应值
        la    	$a0,space
        li    	$v0,4
        syscall				# 输出空格
        addi	$s1,$s1,1		# j = j + 1
	bne	$s1,$t2,print2		# 如果j == 5，跳出循环
	la    	$a0,line
        li    	$v0,4
        syscall	 			# 输出回车
        addi	$s0,$s0,1		# i = i + 1
	bne	$s0,$t2,print1		# 如果i == 5，跳出循环
end:
     	li    	$v0,10
     	syscall 			# 结束程序