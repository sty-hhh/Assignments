module mux2_32b(
  input  [31:0] in0, in1,
  input  sel,
  output [31:0] out
);

assign out = ({32{sel==1'b0}} & in0)//���memtoreg��0��д��ALU�����
           | ({32{sel==1'b1}} & in1);//���memtoreg��1��д��洢���ĳ���1
        
endmodule