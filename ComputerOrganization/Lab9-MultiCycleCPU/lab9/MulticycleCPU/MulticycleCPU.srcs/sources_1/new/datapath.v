`timescale 1ns / 1ps

module datapath(
    input wire clk, reset,
    input wire pcen, irwrite, regwrite,
    input wire alusrca, iord, memtoreg, regdst,
    input wire [1:0] alusrcb, 
    input wire [1:0] pcsrc,
    input wire [2:0] alucontrol, 
    output wire zero,
    output wire [31:0] adr, writedata,
    input wire [31:0] readdata,
    output wire [5:0] op,funct
    );
    wire [4:0] writereg;
    wire [31:0] pcnext, pc;
    wire [31:0] instr, data, srca, srcb;
    wire [31:0] a;
    wire [31:0] aluresult, aluout;
    wire [31:0] signimm; // the sign-extended imm
    wire [31:0] signimmsh; // the sign-extended imm << 2
    wire [31:0] wd3, rd1, rd2;
    assign op = instr[31:26];
    assign funct = instr[5:0];
    // datapath
    flopenr #(32) pcreg(clk, reset, pcen, pcnext, pc);
    mux2 #(32) adrmux(pc, aluout, iord, adr);// 由iord控制adr选择pc还是aluout
    flopenr #(32) instrreg(clk, reset, irwrite, readdata, instr);
    // 寄存器IR 在irwrite==1时触发instr = readdata
    flopr #(32) datareg(clk, reset, readdata, data);
    // 寄存器MDR 触发data = readdata
    mux2 #(5) regdstmux(instr[20:16],instr[15:11], regdst, writereg);
    mux2 #(32) wdmux(aluout, data, memtoreg, wd3);
    regfile rf(clk, regwrite, instr[25:21],instr[20:16],writereg, wd3, rd1, rd2);
    signext se(instr[15:0], signimm);
    sl2 immsh(signimm, signimmsh);
    flopr #(32) areg(clk, reset, rd1, a);// 寄存器A 触发a = rd1
    flopr #(32) breg(clk, reset, rd2, writedata);// 寄存器B 触发writedata = rd2
    mux2 #(32) srcamux(pc, a, alusrca, srca);// 由alusrca控制srca选择a还是pc
    mux4 #(32) srcbmux(writedata, 32'b100, signimm, signimmsh, alusrcb, srcb);
    // 由alusrcb控制srcb选择writedata，4，signimm还是signimmsh
    alu alu(srca, srcb, alucontrol, aluresult, zero);
    flopr #(32) alureg(clk, reset, aluresult, aluout);// 寄存器ALUout 触发aluout = aluresult
    mux3 #(32) pcmux(aluresult, aluout,{pc[31:28], instr[25:0], 2'b00},pcsrc, pcnext);
    // 由pcsrc控制pcnext选择aluresult，aluout还是j指令的跳转地址
endmodule