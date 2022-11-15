	.data
arr1: 	.word  	1:3136
arr2:   .word   1:576
arr3:   .word   1:100
space:	.asciiz	" "
line:   .asciiz "\n"
	.text
	
	addi	$t0,$0,7		# 输入的尺寸为7*7
	addi	$t1,$0,3		# 卷积核的尺寸为3*3 
	addi	$s7,$0,16		# 通道数位为16
	
	move    $s0,$0			# 初始化（循环变量）
     	mul	$s2,$t0,$t0		
     	mul	$s2,$s2,$s7		# 输入大小为7*7*16	
read1:	sll	$t3,$s0,2		
	li    	$v0,5			# 输入一个元素
     	syscall
     	addi	$v0,$v0,1
     	srl	$v0,$v0,1		# A=(a+1)/2
     	sw	$v0,arr1($t3)		# 存入数组对应位置中
     	addi 	$s0,$s0,1
     	bne	$s0,$s2,read1		# 循环次数未到，继续循环
	
     	move    $s0,$0			# 初始化（循环变量）
     	mul	$s2,$t1,$t1		
     	mul	$s2,$s2,$s7		# 卷积核大小为3*3*16
read2:	sll	$t3,$s0,2		
	li    	$v0,5			# 输入一个元素
     	syscall
     	addi	$v0,$v0,1
     	srl	$v0,$v0,1		# B=(b+1)/2
     	sw	$v0,arr2($t3)		# 存入数组对应位置中
     	addi 	$s0,$s0,1
     	bne	$s0,$s2,read2		# 循环次数未到，继续循环

	sub    	$t2,$t0,$t1		
    	addi    $t2,$t2,1    		# 卷积结果的尺寸$t2 = 7 - 3 + 1 = 5
    
     	move    $s0,$0    		# $s0 = i (循环变量)
for1:   move 	$s1,$0			# $s1 = j (循环变量)
for2:   move	$s5,$0			# $s5用于保存count函数后得到的1的数量
	move 	$s2,$0			# $s2 = k (循环变量)
for3:	move	$t6,$0			# $t6用于得出输入张量1与0连起来后的结果
	move	$t7,$0			# $t7用于得出卷积核1与0连起来后的结果
	move 	$s3,$0			# $s3 = l (循环变量)
for4:	move 	$s4,$0			# $s4 = r
for5:	mul	$s6,$t0,$t0
	mul	$s6,$s6,$s2
	add	$t4,$s0,$s3
	mul	$t4,$t4,$t0
	add	$t4,$t4,$s1
	add	$t4,$t4,$s4
	add	$t4,$t4,$s6
	sll	$t4,$t4,2		# $t4 = (i+l)*7+j+r+k*7*7 arr1的偏移量
	
	mul	$s6,$t1,$t1
	mul	$s6,$s6,$s2
	mul	$t5,$s3,$t1
	add	$t5,$t5,$s4
	add	$t5,$t5,$s6
	sll	$t5,$t5,2		# $t5 = l*3+r+k*3*3 arr2的偏移量
	
	lw	$t8,arr1($t4)		# $t7为arr1对应值
	lw	$t9,arr2($t5)		# $t8为arr2对应值
					
	sll	$t6,$t6,1		
	add	$t6,$t6,$t8		# 合并输入张量3*3*1中的1和0
	sll	$t7,$t7,1
	add	$t7,$t7,$t9		# 合并卷积核3*3*1中的1和0
					
	addi	$s4,$s4,1		# r = r + 1
	bne	$s4,$t1,for5		# 如果r == 3，跳出循环
	addi	$s3,$s3,1		# l = l + 1
	bne	$s3,$t1,for4		# 如果l == 3，跳出循环
        xor	$a0,$t6,$t7		# $t6与$t7异或
	jal	count			# 调用count函数，计算1的个数
	add	$s5,$s5,$v0		# 将结果加到$s5中
	addi	$s2,$s2,1		# k = k + 1
	bne	$s2,$s7,for3		# 如果k == 16，跳出循环
			
	mul	$t3,$s0,$t2		
	add	$t3,$t3,$s1
	sll	$t3,$t3,2		# $t3 = i*5+j arr3的偏移量
			
	mul	$s6,$t1,$t1
	mul	$s6,$s6,$s7
	sll	$s5,$s5,1
	sub	$s5,$s5,$s6
	sub	$s5,$0,$s5		# 公式result=N-2*BCNT(XNOR(A*B))
	sw	$s5,arr3($t3)		# 将$s5的值存入arr3对应位置
	
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
     	
count:					# count函数，用于计算一个二进制数中1的个数
	move	$t4,$0			
	addi	$t5,$0,0x00000001	# $t5用于判断二进制数末尾是否是1
	move	$v0,$0			
	addi	$t8,$0,9		# 循环次数
	move	$t9,$0			# 循环变量
loop:	and	$t4,$a0,$t5		# $t4用于保存按位与结果，得到1说明末尾位是1
	add	$v0,$v0,$t4		# 计数
	srl	$a0,$a0,1		# 将二进制数右移一位
	addi	$t9,$t9,1		
	bne	$t9,$t8,loop		# 未到循环次数，继续循环
	jr 	$ra			# 函数返回
