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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; end
      MUL1: begin idx[1]=4; idx[1]=5; idx[1]=6; idx[1]=7; end
      MUL2: begin idx[2]=8; idx[2]=9; idx[2]=10; idx[2]=11; end
      MUL3: begin idx[3]=12; idx[3]=13; idx[3]=14; idx[3]=15; end
    default: begin end
    endcase
  end

endmodule
