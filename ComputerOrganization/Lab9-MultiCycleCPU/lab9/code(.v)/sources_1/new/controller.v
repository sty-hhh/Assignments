`timescale 1ns / 1ps

module controller(
    input wire clk, reset,
    input wire [5:0] op, funct,
    input wire zero,
    output wire pcen, memwrite, irwrite, regwrite,
    output wire alusrca, iord, memtoreg, regdst,
    output wire [1:0] alusrcb, 
    output wire [1:0] pcsrc,
    output wire [2:0] alucontrol,
    output wire [14:0] controls
    ); 
    wire [1:0] aluop; 
    wire pcwritecond, pcwrite;
    maindec md(clk, reset, op, pcwrite, alusrca, alusrcb, memtoreg, regwrite, 
        regdst, memwrite, irwrite, pcsrc, aluop, pcwritecond, iord,controls); 
    aludec ad(funct, aluop, alucontrol);
    assign pcen = pcwrite | (pcwritecond & zero); 
endmodule
