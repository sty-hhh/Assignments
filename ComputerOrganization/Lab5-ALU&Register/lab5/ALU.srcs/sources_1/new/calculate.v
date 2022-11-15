`timescale 1ns / 1ps

module calculate(
    input wire [7:0] num1,
    input wire [2:0] op,
    output reg[31:0] result
    );
    wire [31:0] num2;
    wire [31:0] Sign_extend;
    
    assign num2 = 32'h00000001;
    assign Sign_extend = {{24{1'b0}},num1[7:0]};
    
    always @(op,Sign_extend,num2) begin
        case (op)
            3'b000: result <= Sign_extend + num2;           //op位000，加运算
            3'b001: result <= Sign_extend - num2;           //op位001，减运算
            3'b010: result <= Sign_extend & num2;           //op位010，与运算
            3'b011: result <= Sign_extend | num2;           //op位011，或运算
            3'b100: result <= ~Sign_extend;                 //op位100，num1取反
            3'b101: result <= Sign_extend < num2 ? 1:0;     //op位101，SLT运算
            default: result <= 0;                           //否则返回0
        endcase
    end            
endmodule
