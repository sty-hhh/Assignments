module mux2_32b(
  input  [31:0] in0, in1,
  input  sel,
  output [31:0] out
);

assign out = ({32{sel==1'b0}} & in0)//如果memtoreg是0，写入ALU的输出
           | ({32{sel==1'b1}} & in1);//如果memtoreg是1，写入存储器的常数1
        
endmodule