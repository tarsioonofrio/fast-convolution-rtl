//-------------------------------------------------------------------------
// Index multiplexer module for selecting register indices based on state
//-------------------------------------------------------------------------

package pack_mux_mult;
  parameter int NMULT = {num_mult};
  parameter int SMULT = {state_mult};
endpackage


module MuxMult
  (
    input  logic[$clog2({state_mult}-1):0] idx_in, // current state
    output logic[$clog2({state_mult}*{num_mult}-1):0] idx_out[0:{num_mult}-1]  // index array output
  );

  timeunit 1ns;
  timeprecision 1ps;

  always_comb begin
    unique case (idx_in)
{case}
    endcase
  end

endmodule
