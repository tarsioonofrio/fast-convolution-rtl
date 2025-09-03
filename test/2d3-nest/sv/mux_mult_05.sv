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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; end
      MUL1: begin idx[1]=5; idx[1]=6; idx[1]=7; idx[1]=8; idx[1]=9; end
      MUL2: begin idx[2]=10; idx[2]=11; idx[2]=12; idx[2]=13; idx[2]=14; end
      MUL3: begin idx[3]=15; idx[3]=16; idx[3]=17; idx[3]=18; idx[3]=19; end
      MUL4: begin idx[4]=20; idx[4]=21; idx[4]=22; idx[4]=23; idx[4]=24; end
    default: begin end
    endcase
  end

endmodule
