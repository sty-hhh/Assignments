`timescale 1ns / 1ps

module display(
    input wire clk,reset,
    input wire [31:0]s,
    output wire [6:0]seg,
    output reg [3:0]ans
    );
    reg [20:0]count;
    reg [4:0]digit; 
    always@(posedge clk,posedge reset)
    if(reset)  
        count = 0;
    else 
        count = count + 1;
       
    always @(posedge clk)
    case(count[20:19])
        0:begin
            ans = 4'b1110;
            digit = s[3:0];
        end
        
        1:begin
            ans = 4'b1101;
            digit = s[7:4];
        end

        2:begin
            ans = 4'b1011;
            digit =s[11:8];
        end
        
        3:begin
            ans = 4'b0111;
            digit = s[15:12];
        end
    endcase
    
    seg7 U4(.din(digit),.dout(seg));
endmodule

