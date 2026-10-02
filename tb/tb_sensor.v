`timescale 1ns/1ps

module tb_sensor;
    reg clk = 0;
    reg rst = 1;
    reg sleep_mode = 0;
    reg [7:0] data_in = 0;
    wire [7:0] data_out;

    sensor_node uut (
        .clk(clk),
        .rst(rst),
        .sleep_mode(sleep_mode),
        .data_in(data_in),
        .data_out(data_out)
    );

    always #5 clk = ~clk;

    integer i;
    initial begin
        $dumpfile(`VCD_FILE);
        $dumpvars(0, tb_sensor);
        #20 rst = 0;

        for (i = 0; i < 50; i = i + 1) begin
            @(posedge clk);
            data_in = (i == 15) ? 8'hDE : ($random & 8'hFF);
        end

        sleep_mode = 1;
        for (i = 0; i < 100; i = i + 1) begin
            @(posedge clk);
        end
        $finish;
    end
endmodule
