//-------------------------------------------------------------------------
// Index multiplexer module for selecting register indices based on state
//-------------------------------------------------------------------------

package pack_mux_mult;
  parameter int NUM_MULT = 4;
  parameter int STATE_MULT = 2;
endpackage


module MuxMult
  (
    input  logic[$clog2(2-1):0] idx_in, // current state
    output logic[$clog2(2*4-1):0] idx_out[0:4-1]  // index array output
  );

  timeunit 1ns;
  timeprecision 1ps;

  always_comb begin
    unique case (idx_in)
      default: begin idx_out[0]=0; idx_out[1]=1; idx_out[2]=2; idx_out[3]=3; end
      1: begin idx_out[0]=4; idx_out[1]=5; idx_out[2]=6; idx_out[3]=7; end
    endcase
  end

endmodule
