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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; idx[0]=5; idx[0]=6; idx[0]=7; end
      MUL1: begin idx[1]=8; idx[1]=9; idx[1]=10; idx[1]=11; idx[1]=12; idx[1]=13; idx[1]=14; idx[1]=15; end
    default: begin end
    endcase
  end

endmodule
