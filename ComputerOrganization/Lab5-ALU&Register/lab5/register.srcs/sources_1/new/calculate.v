`timescale 1ns / 1ps

module calculate(
    input wire [31:0] num1,
    input wire [31:0] num2,
    input wire [2:0] op,
    output reg[31:0] result
    );

    always @(op,num1,num2) begin
        case (op)
            3'b000: result <= num1 + num2;           //op位000，加运算
            3'b001: result <= num1 - num2;           //op位001，减运算
            3'b010: result <= num1 & num2;           //op位010，与运算
            3'b011: result <= num1 | num2;           //op位011，或运算
            3'b100: result <= ~num1;                 //op位100，num1取反
            3'b101: result <= num1 < num2 ? 1:0;     //op位101，SLT运算
            default: result <= 0;                           //否则返回0
        endcase
    end            
endmodule