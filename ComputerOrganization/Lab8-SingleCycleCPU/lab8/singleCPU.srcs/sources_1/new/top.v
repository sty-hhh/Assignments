`timescale 1ns / 1ps

module top(
	input wire clk,rst,
	output wire[31:0] writedata,dataadr,
	output wire memwrite
    );
	wire[31:0] pc,instr,readdata;
	mips mips(clk,rst,pc,instr,memwrite,dataadr,writedata,readdata);
    //create imem and dmem by yourself
	inst_mem imem(clk,pc[9:2],instr);
	data_mem dmem(~clk,memwrite,dataadr[9:2],writedata,readdata);
endmodule