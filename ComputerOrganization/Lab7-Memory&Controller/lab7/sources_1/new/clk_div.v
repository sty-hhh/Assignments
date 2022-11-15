`timescale 1ns / 1ps

module clk_div(
    input wire clk,rst,
    output reg clk1
    );
    reg [26:0]count;
    initial clk1 <= 0;
    always@(posedge clk or negedge rst)
        if(rst) begin
            count <= 0;
            clk1 <= 0;
        end    
        else begin
            if(count[26]) begin
                count <= 0;
                clk1 <= ~clk1;
            end
            else
                count <= count + 1;
        end
endmodule
