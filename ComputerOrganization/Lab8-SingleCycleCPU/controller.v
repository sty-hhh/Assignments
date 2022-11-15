`timescale 1ns / 1ps

module controller(
	input wire[5:0] op,funct,
	input wire zero,
	output wire memtoreg,memwrite,
	output wire pcsrc,alusrc,
	output wire regdst,regwrite,
	output wire jump,
	output wire[2:0] alucontrol
    );
	wire[1:0] aluop;
	wire branch;

	maindec md(op,memtoreg,memwrite,branch,alusrc,regdst,regwrite,jump,aluop);
	aludec ad(funct,aluop,alucontrol);

	assign pcsrc = branch & zero;
endmodule
