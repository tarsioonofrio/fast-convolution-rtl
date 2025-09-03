//-------------------------------------------------------------------------
// Index multiplexer module for selecting register indices based on state
//-------------------------------------------------------------------------

module MuxMult
  import packConv::*;
(
  input  state_type current_st,  // current state
  output logic[5:0] idx[0:NMULT-1]    // index array output
);

  always_comb begin
    unique case (current_st)
      MULT0: begin idx[0]=0; end
      MULT1: begin idx[0]=1; end
      MULT2: begin idx[0]=2; end
      MULT3: begin idx[0]=3; end
      MULT4: begin idx[0]=4; end
    default: begin end
    endcase
  end

endmodule
