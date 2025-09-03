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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; idx[0]=5; idx[0]=6; idx[0]=7; idx[0]=8; idx[0]=9; idx[0]=10; idx[0]=11; idx[0]=12; idx[0]=13; idx[0]=14; idx[0]=15; idx[0]=16; idx[0]=17; idx[0]=18; idx[0]=19; idx[0]=20; idx[0]=21; idx[0]=22; idx[0]=23; idx[0]=24; end
    default: begin end
    endcase
  end

endmodule
