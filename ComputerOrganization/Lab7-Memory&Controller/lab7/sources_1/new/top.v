`timescale 1ns / 1ps

module top(
    input clk,rst,
    output [3:0] ans, //select for seg
    output [6:0] seg, //segment digital
    output wire memtoreg,memwrite,
    output wire pcsrc,alusrc,
    output wire regdst,regwrite,
    output wire jump,branch,
    output wire [2:0] alucontrol
    );
    wire [7:0] addr;
    wire clk1;//��Ƶ���clk
    wire [31:0] inst;//32λָ��
    wire [15:0] inst1;
    wire [5:0] op;
    wire [5:0] funct;
    wire zero;
    
    assign inst1 = inst[15:0];//ָ���16λ������display
    assign op = inst[31:26];//opȡָ���6λ
    assign funct = inst[5:0];//functȡָ���6λ
    assign zero = 1;//��ʵ��û��ALU���������Ĭ����Ϊ1
    
    clk_div cd(.clk(clk),.rst(rst),.clk1(clk1));
    pc p(.clk(clk1),.rst(rst),.addr(addr));
    Ins_Rom rom(.clka(clk1),.addra(addr),.douta(inst));
    controller con(
        .op(op),
        .funct(funct),
        .zero(zero),
        .memtoreg(memtoreg),
        .memwrite(memwrite),
        .pcsrc(pcsrc),
        .alusrc(alusrc),
        .regdst(regdst),
        .regwrite(regwrite),
        .jump(jump),
        .branch(branch),
        .alucontrol(alucontrol)
    );
    display U2(.clk(clk),.reset(rst),.s(inst1),.ans(ans),.seg(seg));
endmodule