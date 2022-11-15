`timescale 1ns / 1ps

module top(
    input clk,
    input rst,
    input [7:0] addr,
    output [3:0] ans, //select for seg
    output [6:0] seg  //segment digital
    );
    wire [31:0] data;
    wire [15:0] data1;
    assign data1=data[15:0];
    Ins_Rom rom(
        .clka(clk),
        .addra(addr),
        .douta(data)
        );
    display U2(.clk(clk),.reset(rst),.s(data1),.ans(ans),.seg(seg));
endmodule