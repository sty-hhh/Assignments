`timescale 1ns / 1ps

module top(
    input clk,
    input rst,
    input [2:0] op,
    input [7:0] num1,
    output [3:0] ans, //select for seg
    output [6:0] seg  //segment digital
    );
    wire [31:0] s;
    calculate U1(.num1(num1),.op(op),.result(s));
    
    display U2(.clk(clk),.reset(rst),.s(s),.ans(ans),.seg(seg));
endmodule
