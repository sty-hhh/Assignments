`timescale 1ns / 1ps

module top(
    input clk,
    input rst,
    input [3:0] ra_addr,
    input [3:0] rb_addr,
    input [3:0] rd_addr,
    input sel,//选择读或者写              
    input memtoreg,//选择写存储器的常数还是ALU的输出
    output [3:0] ans, //select for seg
    output [6:0] seg  //segment digital
    );
    wire [31:0] s;
    wire [31:0] mem0;
    wire [31:0] ra_data;
    wire [31:0] rb_data;
    wire [31:0] rd_data;
    wire we;
    wire [2:0] op;
    
    assign mem0=32'h00000001;//存储器的常数设为1
    assign we=sel;
    assign op=0;//默认为加法
    regfile U4(
        .clk(clk),
        .raddr1(ra_addr),
        .rdata1(ra_data),
        .raddr2(rb_addr),
        .rdata2(rb_data),
        .we(we),
        .waddr(rd_addr),
        .wdata(rd_data)
    );
    calculate U1(.num1(ra_data),.num2(rb_data),.op(op),.result(s));
    mux2_32b U3(.in0(s),.in1(mem0),.sel(memtoreg),.out(rd_data));
    display U2(.clk(clk),.reset(rst),.s(s),.ans(ans),.seg(seg));
endmodule