`timescale 1ns / 1ps

module pc(
    input  clk,rst,
    output reg[7:0]addr
    );
    initial addr <= 0;//初始化地址为0
    always@(posedge clk or negedge rst)  
        begin  
            if (rst) addr <= 0;  //如果reset地址跳到0
            else addr <= addr + 1;  // 跳转到下一指令
        end      
endmodule