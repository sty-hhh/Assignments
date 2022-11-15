`timescale 1ns / 1ps

module maindec(
    input wire clk, reset,
    input wire [5:0] op,
    output wire pcwrite, alusrca,
    output wire [1:0] alusrcb,
    output wire memtoreg, regwrite, regdst, memwrite, irwrite, 
    output wire [1:0] pcsrc,
    output wire [1:0] aluop, 
    output wire pcwritecond, iord,
    output reg [14:0] controls
    ); 
    localparam IFetch=0,RFetch=1,BrFinish=2,JumpFinish=3,AddiExec=4,
        AddiFinish=5,RExec=6,RFinish=7,MemAdr=8,swFinish=9,MemFetch=10,lwFinish=11;
    localparam RTYPE=6'b000000,LW=6'b100011,SW=6'b101011,
        BEQ=6'b000100,ADDI=6'b001000,J=6'b000010,ORI=6'b001101;
    reg [3:0] state,nextstate;
    always@(negedge clk or posedge reset) 
        begin
            if (reset==1) state <= IFetch;
            else state <= nextstate;
        end
    // next state logic
    always @( * )
        case(state)
            IFetch: nextstate <= RFetch;
            RFetch: case(op)
                LW: nextstate <= MemAdr;
                SW: nextstate <= MemAdr;
                RTYPE: nextstate <= RExec;
                BEQ: nextstate <= BrFinish;
                ADDI: nextstate <= AddiExec;
                J: nextstate <= JumpFinish;
                default: nextstate <= IFetch;
            endcase
            BrFinish: nextstate <= IFetch;
            JumpFinish: nextstate <= IFetch;
            AddiExec: nextstate <= AddiFinish;
            AddiFinish: nextstate <= IFetch;
            RExec: nextstate <= RFinish;
            RFinish: nextstate <= IFetch;
            MemAdr: case(op)
                //RTYPE: nextstate <= swFinish;//
                LW: nextstate <= MemFetch;
                SW: nextstate <= swFinish;
                default: nextstate <= IFetch;
            endcase
            swFinish: nextstate <= IFetch;
            MemFetch: nextstate <= lwFinish;
            lwFinish: nextstate <= IFetch;
            default: nextstate <= IFetch;
        endcase
    // output logic
    assign {pcwrite,alusrca,alusrcb,memtoreg,regwrite,regdst,
        memwrite,irwrite, pcsrc,aluop,pcwritecond,iord} = controls;
    always @( * )
        case(state)
            IFetch: controls <= 15'b100100001000000;
            RFetch: controls <= 15'b001100000000000;
            BrFinish: controls <= 15'b010000000010110;
            JumpFinish: controls <= 15'b100000000100000;
            AddiExec: controls <= 15'b011000000000000;
            AddiFinish: controls <= 15'b011001000000000;
            RExec: controls <= 15'b010000100001000;
            RFinish: controls <= 15'b010001100001000;
            MemAdr: controls <= 15'b011000000000001;
            swFinish: controls <= 15'b011000010000001;
            MemFetch: controls <= 15'b011010000000001;
            lwFinish: controls <= 15'b011011000000001;
            default: controls <= 15'b000000000000000;
        endcase
endmodule
