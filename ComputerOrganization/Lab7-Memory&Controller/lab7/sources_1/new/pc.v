`timescale 1ns / 1ps

module pc(
    input  clk,rst,
    output reg[7:0]addr
    );
    initial addr <= 0;//��ʼ����ַΪ0
    always@(posedge clk or negedge rst)  
        begin  
            if (rst) addr <= 0;  //���reset��ַ����0
            else addr <= addr + 1;  // ��ת����һָ��
        end      
endmodule