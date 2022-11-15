`timescale 1ns / 1ps

module flopenr # (parameter WIDTH = 8)(
	input wire clk,rst,
	input wire en,
	input wire[WIDTH-1:0] d,
	output reg[WIDTH-1:0] q
    );
	always @(negedge clk,posedge rst) begin
		if(rst) begin
			q <= 0;
		end else begin
		    if (en)
			    q <= d;
			else
			    q <= q;
		end
	end
endmodule
