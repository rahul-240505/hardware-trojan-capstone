`timescale 1ns/1ps

module tb_rs232;
    reg clk = 0;
    reg rst = 1;
    reg sleep_mode = 0;
    reg tx_start = 0;
    reg [7:0] tx_data = 8'h00;
    wire tx_line;
    wire tx_busy;
    wire [7:0] rx_latch;

    rs232_uart uut (
        .clk(clk),
        .rst(rst),
        .sleep_mode(sleep_mode),
        .tx_start(tx_start),
        .tx_data(tx_data),
        .tx_line(tx_line),
        .tx_busy(tx_busy),
        .rx_latch(rx_latch)
    );

    always #5 clk = ~clk;

    integer i;
    initial begin
        $dumpfile(`VCD_FILE);
        $dumpvars(0, tb_rs232);
        #20 rst = 0;

        // Phase 1: Active UART transmission bursts (100 cycles)
        for (i = 0; i < 100; i = i + 1) begin
            @(posedge clk);
            tx_start = (i % 20 == 0) ? 1'b1 : 1'b0;
            // Inject secret trigger byte (0x99 -> scrambled_check == 0xC3) at cycle 20
            tx_data = (i == 20) ? 8'h99 : ((i * 8'h1F) ^ 8'h3D);
        end

        // Phase 2: Enter Low-Power Sleep Mode (100 cycles)
        sleep_mode = 1;
        tx_start = 0;
        for (i = 0; i < 100; i = i + 1) begin
            @(posedge clk);
            // Residual input bus jitter on shared pins during sleep
            tx_data = (i * 8'h13) ^ 8'hA7;
        end

        $finish;
    end
endmodule
