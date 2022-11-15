`timescale 1ns / 1ps

module datapath(
	input wire clk,rst,
	input wire memtoreg,pcsrc,
	input wire alusrc,regdst,
	input wire regwrite,jump,
	input wire[2:0] alucontrol,
	output wire overflow,zero,
	output wire[31:0] pc,
	input wire[31:0] instr,
	output wire[31:0] aluout,writedata,
	input wire[31:0] readdata
    );
	wire [4:0] writereg;
	wire [31:0] pcnext,pcnextbr,pcplus4,pcbranch;
	wire [31:0] signimm,signimmsh,srca,srcb,result;	
	// next PC
	flopr#(32) pcreg(clk,rst,pcnext,pc);// ����rst��������ʱ������ʱpc = pcnext
	adder pcadd1(pc,32'b100,pcplus4);// pcplus4 = pc + 4
	sl2 immsh(signimm,signimmsh);// signimmsh = signimm << 2
	adder pcadd2(pcplus4,signimmsh,pcbranch);// pcbranch = pcplus4 + signimmsh
	mux2 #(32) pcbrmux(pcplus4,pcbranch,pcsrc,pcnextbr);// ���pcsrc = 1����ôpcnextbr = pcbranch����ת������������pcnextbr = pcplus4(��������)
	mux2 #(32) pcmux(pcnextbr,{pcplus4[31:28],instr[25:0],2'b00},jump,pcnext);//���jump = 1��pcnext��������*4�͵�ǰ��ַ��4λ��ɣ�����pcnext = pcnextbr
	// register
	regfile rf(clk,regwrite,instr[25:21],instr[20:16],writereg,result,srca,writedata);// �ɼĴ������srca��ALU��һ�����룩��writedata
	mux2 #(5) wrmux(instr[20:16],instr[15:11],regdst,writereg);// ����regdst�õ���ȷ��д��ַ
	mux2 #(32) resmux(aluout,readdata,memtoreg,result);// ����memtoregѡ��д�������result��alu���������datamemory��readdata
	signext se(instr[15:0],signimm);// signimm��instr��16λ��32λ��չ
	// ALU
	mux2 #(32) srcbmux(writedata,signimm,alusrc,srcb);// ����alusrcѡ��srcb��ALU�ڶ������룩�����ԼĴ�����writedata����signimm����������չ��
	alu alu(srca,srcb,alucontrol,aluout,overflow,zero);// alu���㣬zero���ڿ������ж��Ƿ�����ת
endmodule