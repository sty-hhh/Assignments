`timescale 1ns / 1ps

module calculate(
    input wire [31:0] num1,
    input wire [31:0] num2,
    input wire [2:0] op,
    output reg[31:0] result
    );

    always @(op,num1,num2) begin
        case (op)
            3'b000: result <= num1 + num2;           //opλ000��������
            3'b001: result <= num1 - num2;           //opλ001��������
            3'b010: result <= num1 & num2;           //opλ010��������
            3'b011: result <= num1 | num2;           //opλ011��������
            3'b100: result <= ~num1;                 //opλ100��num1ȡ��
            3'b101: result <= num1 < num2 ? 1:0;     //opλ101��SLT����
            default: result <= 0;                           //���򷵻�0
        endcase
    end            
endmodule