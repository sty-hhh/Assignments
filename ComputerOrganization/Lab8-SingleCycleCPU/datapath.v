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
	flopr#(32) pcreg(clk,rst,pcnext,pc);// 除非rst，否则在时钟跳变时pc = pcnext
	adder pcadd1(pc,32'b100,pcplus4);// pcplus4 = pc + 4
	sl2 immsh(signimm,signimmsh);// signimmsh = signimm << 2
	adder pcadd2(pcplus4,signimmsh,pcbranch);// pcbranch = pcplus4 + signimmsh
	mux2 #(32) pcbrmux(pcplus4,pcbranch,pcsrc,pcnextbr);// 如果pcsrc = 1，那么pcnextbr = pcbranch（跳转发生），否则pcnextbr = pcplus4(正常运行)
	mux2 #(32) pcmux(pcnextbr,{pcplus4[31:28],instr[25:0],2'b00},jump,pcnext);//如果jump = 1，pcnext由立即数*4和当前地址高4位组成，否则pcnext = pcnextbr
	// register
	regfile rf(clk,regwrite,instr[25:21],instr[20:16],writereg,result,srca,writedata);// 由寄存器获得srca（ALU第一个输入）和writedata
	mux2 #(5) wrmux(instr[20:16],instr[15:11],regdst,writereg);// 根据regdst得到正确的写地址
	mux2 #(32) resmux(aluout,readdata,memtoreg,result);// 根据memtoreg选择写入的数据result是alu的输出还是datamemory的readdata
	signext se(instr[15:0],signimm);// signimm是instr低16位的32位扩展
	// ALU
	mux2 #(32) srcbmux(writedata,signimm,alusrc,srcb);// 根据alusrc选择srcb（ALU第二个输入）是来自寄存器的writedata还是signimm（立即数扩展）
	alu alu(srca,srcb,alucontrol,aluout,overflow,zero);// alu计算，zero用于控制器判断是否发生跳转
endmodule