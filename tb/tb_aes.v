`timescale 1ns/1ps
module tb_aes;
    reg clk = 0;
    reg rst = 1;
    reg sleep_mode = 0;
    reg [15:0] state_in = 16'h0000;
    reg [15:0] round_key = 16'h2B7E;
    wire [15:0] state_out;

    aes_t1800 uut (
        .clk(clk), .rst(rst), .sleep_mode(sleep_mode),
        .state_in(state_in), .round_key(round_key), .state_out(state_out)
    );

    always #5 clk = ~clk;
    integer i;
    initial begin
        $dumpfile(`VCD_FILE);
        $dumpvars(0, tb_aes);
        #20 rst = 0;
        for (i = 0; i < 80; i = i + 1) begin
            @(posedge clk);
            state_in = (i == 15) ? 16'hDEAD : ((i * 16'h193B) ^ 16'h5A5A);
            round_key = (i * 16'h0F0F) ^ 16'h3C6E;
        end
        sleep_mode = 1;
        for (i = 0; i < 100; i = i + 1) begin
            @(posedge clk);
        end
        $finish;
    end
endmodule
