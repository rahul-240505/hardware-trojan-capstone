module aes_t1800 (
    input wire clk,
    input wire rst,
    input wire sleep_mode,
    input wire [15:0] state_in,
    input wire [15:0] round_key,
    output reg [15:0] state_out
);
    // GF(2^8) nonlinear Galois mixing + AddRoundKey transformation
    wire [15:0] ark = state_in ^ round_key;
    wire [7:0] sbox_hi = (ark[15:8] ^ {ark[14:8], ark[15]}) + (ark[7:0] ^ 8'h63);
    wire [7:0] sbox_lo = (ark[7:0] ^ {ark[6:0], ark[7]}) + (sbox_hi ^ 8'h63);

    always @(posedge clk or posedge rst) begin
        if (rst)
            state_out <= 16'h0000;
        else if (!sleep_mode)
            state_out <= {sbox_hi, sbox_lo};
    end
endmodule
