`timescale 1ns / 1ps

module mips(
	input wire clk,rst,
	output wire[31:0] pc,
	input wire[31:0] instr,
	output wire memwrite,
	output wire[31:0] aluout,writedata,
	input wire[31:0] readdata 
    );
	
	wire memtoreg,alusrc,regdst,regwrite,jump,pcsrc,zero,overflow;
	wire[2:0] alucontrol;

	controller c(instr[31:26],instr[5:0],zero,memtoreg,
		memwrite,pcsrc,alusrc,regdst,regwrite,jump,alucontrol);
	datapath dp(clk,rst,memtoreg,pcsrc,alusrc,
		regdst,regwrite,jump,alucontrol,overflow,zero,pc,instr,aluout,writedata,readdata);
	
endmodule