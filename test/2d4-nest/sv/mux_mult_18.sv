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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; idx[0]=5; idx[0]=6; idx[0]=7; idx[0]=8; idx[0]=9; idx[0]=10; idx[0]=11; idx[0]=12; idx[0]=13; idx[0]=14; idx[0]=15; idx[0]=16; idx[0]=17; end
      MUL1: begin idx[1]=18; idx[1]=19; idx[1]=20; idx[1]=21; idx[1]=22; idx[1]=23; idx[1]=24; idx[1]=25; idx[1]=26; idx[1]=27; idx[1]=28; idx[1]=29; idx[1]=30; idx[1]=31; idx[1]=32; idx[1]=33; idx[1]=34; idx[1]=35; end
    default: begin end
    endcase
  end

endmodule
