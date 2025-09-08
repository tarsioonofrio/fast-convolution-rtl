//-------------------------------------------------------------------------
// Index multiplexer module for selecting register indices based on state
//-------------------------------------------------------------------------

package pack_mux_mult;
  parameter int NMULT = {num_mult};
  parameter int SMULT = {state_mult};
endpackage


module MuxMult
  import pack_mux_mult::*;
  (
    input  state_type current_st,  // current state
    output logic[5:0] idx[0:NMULT-1]    // index array output
  );

  timeunit 1ns;
  timeprecision 1ps;

  always_comb begin
    unique case (current_st)
{case}
    endcase
  end

endmodule
