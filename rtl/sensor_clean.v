module sensor_node (
    input wire clk,
    input wire rst,
    input wire sleep_mode,
    input wire [7:0] data_in,
    output reg [7:0] data_out
);
    always @(posedge clk or posedge rst) begin
        if (rst)
            data_out <= 8'b0;
        else if (!sleep_mode)
            data_out <= (data_in ^ 8'hA5) + 8'd3;
    end
endmodule
