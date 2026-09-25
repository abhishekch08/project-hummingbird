// CH05 illustrative reference for the continuous-clock *comparison* only.
// The clk_time_i source and reset release are external contracts. clk_time_i
// MUST remain alive during system sleep for this alternative. capture_i MUST be
// synchronous to clk_time_i and held long enough; no CDC, reset crossing,
// metastability MTBF, wake handoff, host-epoch, IMU or trigger matrix is built here.
// This block has not been compiled, formally verified or mapped to a foundry.
module ch05_continuous_reference (
    input  logic        clk_time_i,
    input  logic        rst_ni,
    input  logic        capture_i,
    output logic [63:0] monotonic_ticks_o,
    output logic [63:0] capture_ticks_o,
    output logic        capture_valid_o,
    output logic        overflow_o
);

  always_ff @(posedge clk_time_i or negedge rst_ni) begin
    if (!rst_ni) begin
      monotonic_ticks_o <= 64'b0;
      capture_ticks_o   <= 64'b0;
      capture_valid_o   <= 1'b0;
      overflow_o        <= 1'b0;
    end else begin
      capture_valid_o <= 1'b0;
      if (!overflow_o) begin
        if (&monotonic_ticks_o) begin
          overflow_o <= 1'b1; // Saturate and reject captures; never roll over.
        end else begin
          monotonic_ticks_o <= monotonic_ticks_o + 64'd1;
          if (capture_i) begin
            capture_ticks_o <= monotonic_ticks_o + 64'd1;
            capture_valid_o <= 1'b1;
          end
        end
      end
    end
  end
endmodule
