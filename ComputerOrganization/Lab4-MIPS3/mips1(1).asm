     	.data
K:   	.word   0
Y:  	.word   56
Z:	.space 	200		# ������Z����50*4=200���ֽڵĿռ�
str: 	.asciiz "  "
        .text
main:
	lw	$s1,K		# $s1����K
	lw	$s2,Y		# $s2����Y
	la 	$s3,Z		# $s3��������Z
loop:
	slti 	$t0,$s1,50	# ��K<50��$t0 = 1������$t0 = 0
	beq 	$t0,$0,exit	# ��$t0 = 0����K>=50������ת��exit������ѭ����
	srl 	$t1,$s1,2	# ��$s1������λ����$t1 = K / 4
	addi	$t1,$t1,210	# $t1 = $t1 + 210
	sll	$t1,$t1,4	# ��$t1����4λ����$t1 = $t1 * 16
	sub	$t1,$s2,$t1	# $t1 = $s2(Y) - $t1
	sw	$t1,0($s3)	# ��$t1��ֵ����$s3(����Z)����Ӧλ����
	lw	$a0,0($s3)	# �������Z��ǰλ�õ�ֵ
	li	$v0,1
	syscall
	la 	$a0,str		# ����ո� ��
	li	$v0,4
	syscall
	addi	$s3,$s3,4	# ������ZѰַ����һ��λ�ã�4���ֽڣ�
	addi	$s1,$s1,1	# K = K + 1
	j	loop		# ��ת��loop������ѭ��
exit:
	li	$v0,10		# ������ֹ����
	syscall
