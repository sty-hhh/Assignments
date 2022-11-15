`timescale 1ns / 1ps

module testbench();
	reg clk;
	reg rst;
	wire[31:0] writedata,adr;
	wire memwrite;
    wire [14:0]controls;
	top dut(clk,rst,writedata,adr,memwrite,controls);
	initial begin 
		rst <= 1;
		#100;
		rst <= 0;
	end
    // ����ʱ��������1/5�����𵽶����ڼӿ������ٶȵ�����
	always begin
		clk <= 1;
		#2;
		clk <= 0;
		#2;
	end
	always @(negedge clk) begin
		if(memwrite) begin
			if(writedata === 7 & adr === 84) begin
				$display("Simulation succeeded");
				$stop;
			end
		end
	end
endmodule

