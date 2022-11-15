`timescale 1ns / 1ps

module mips(
    input wire clk, reset,
    output wire [31:0] adr, writedata,
    output wire memwrite,
    input wire [31:0] readdata,
    output wire [14:0] controls
    );
    wire zero, pcen, irwrite, regwrite,alusrca, iord, memtoreg, regdst;
    wire [1:0] alusrcb;
    wire [1:0] pcsrc;
    wire [2:0] alucontrol;
    wire [5:0] op,funct;
    controller c(clk,reset,op,funct,zero,pcen,memwrite,irwrite,regwrite,
        alusrca,iord,memtoreg,regdst,alusrcb,pcsrc,alucontrol,controls); 
    datapath dp(clk,reset,pcen,irwrite,regwrite,alusrca,iord,memtoreg,regdst,
        alusrcb,pcsrc,alucontrol,zero,adr,writedata,readdata,op,funct);
endmodule