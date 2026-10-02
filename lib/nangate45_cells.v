`timescale 1ns/1ps

module INV_X1 (input A, output ZN); assign ZN = ~A; endmodule
module BUF_X1 (input A, output Z); assign Z = A; endmodule
module AND2_X1 (input A1, A2, output ZN); assign ZN = A1 & A2; endmodule
module AND3_X1 (input A1, A2, A3, output ZN); assign ZN = A1 & A2 & A3; endmodule
module AND4_X1 (input A1, A2, A3, A4, output ZN); assign ZN = A1 & A2 & A3 & A4; endmodule
module NAND2_X1 (input A1, A2, output ZN); assign ZN = ~(A1 & A2); endmodule
module NAND3_X1 (input A1, A2, A3, output ZN); assign ZN = ~(A1 & A2 & A3); endmodule
module NAND4_X1 (input A1, A2, A3, A4, output ZN); assign ZN = ~(A1 & A2 & A3 & A4); endmodule
module OR2_X1 (input A1, A2, output ZN); assign ZN = A1 | A2; endmodule
module OR3_X1 (input A1, A2, A3, output ZN); assign ZN = A1 | A2 | A3; endmodule
module OR4_X1 (input A1, A2, A3, A4, output ZN); assign ZN = A1 | A2 | A3 | A4; endmodule
module NOR2_X1 (input A1, A2, output ZN); assign ZN = ~(A1 | A2); endmodule
module NOR3_X1 (input A1, A2, A3, output ZN); assign ZN = ~(A1 | A2 | A3); endmodule
module NOR4_X1 (input A1, A2, A3, A4, output ZN); assign ZN = ~(A1 | A2 | A3 | A4); endmodule
module XOR2_X1 (input A, B, output Z); assign Z = A ^ B; endmodule
module XNOR2_X1 (input A, B, output ZN); assign ZN = ~(A ^ B); endmodule
module MUX2_X1 (input A, B, S, output Z); assign Z = S ? B : A; endmodule
module AOI21_X1 (input B1, B2, A, output ZN); assign ZN = ~((B1 & B2) | A); endmodule
module AOI22_X1 (input A1, A2, B1, B2, output ZN); assign ZN = ~((A1 & A2) | (B1 & B2)); endmodule
module AOI211_X1 (input C1, C2, B, A, output ZN); assign ZN = ~((C1 & C2) | B | A); endmodule
module OAI21_X1 (input B1, B2, A, output ZN); assign ZN = ~((B1 | B2) & A); endmodule
module OAI22_X1 (input A1, A2, B1, B2, output ZN); assign ZN = ~((A1 | A2) & (B1 | B2)); endmodule
module OAI211_X1 (input C1, C2, B, A, output ZN); assign ZN = ~((C1 | C2) & B & A); endmodule

module DFF_X1 (input D, CK, output reg Q, output QN);
    assign QN = ~Q;
    always @(posedge CK) Q <= D;
endmodule

module DFFR_X1 (input D, CK, RN, output reg Q, output QN);
    assign QN = ~Q;
    always @(posedge CK or negedge RN)
        if (!RN) Q <= 1'b0;
        else Q <= D;
endmodule

module DFFS_X1 (input D, CK, SN, output reg Q, output QN);
    assign QN = ~Q;
    always @(posedge CK or negedge SN)
        if (!SN) Q <= 1'b1;
        else Q <= D;
endmodule

module DFFRS_X1 (input D, CK, RN, SN, output reg Q, output QN);
    assign QN = ~Q;
    always @(posedge CK or negedge RN or negedge SN)
        if (!RN) Q <= 1'b0;
        else if (!SN) Q <= 1'b1;
        else Q <= D;
endmodule
