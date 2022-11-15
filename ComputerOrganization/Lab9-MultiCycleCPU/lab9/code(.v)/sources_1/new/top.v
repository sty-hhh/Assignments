`timescale 1ns / 1ps

module top(
    input wire clk, reset,
    output wire [31:0] writedata, adr,
    output wire memwrite,
    output wire [14:0]controls
    );
    wire [31:0] readdata;
    // instantiate processor and memory
    mips mips(clk, reset, adr, writedata, memwrite,readdata,controls);
    idmem idmem(clk, memwrite, adr[9:2], writedata,readdata);
endmodule

