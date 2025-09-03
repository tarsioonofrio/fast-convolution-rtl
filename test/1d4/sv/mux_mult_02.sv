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
      MUL0: begin idx[0]=0; idx[0]=1; end
      MUL1: begin idx[1]=2; idx[1]=3; end
      MUL2: begin idx[2]=4; idx[2]=5; end
    default: begin end
    endcase
  end

endmodule
