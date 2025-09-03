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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; idx[0]=5; idx[0]=6; idx[0]=7; idx[0]=8; idx[0]=9; idx[0]=10; idx[0]=11; end
      MUL1: begin idx[1]=12; idx[1]=13; idx[1]=14; idx[1]=15; idx[1]=16; idx[1]=17; idx[1]=18; idx[1]=19; idx[1]=20; idx[1]=21; idx[1]=22; idx[1]=23; end
      MUL2: begin idx[2]=24; idx[2]=25; idx[2]=26; idx[2]=27; idx[2]=28; idx[2]=29; idx[2]=30; idx[2]=31; idx[2]=32; idx[2]=33; idx[2]=34; idx[2]=35; end
    default: begin end
    endcase
  end

endmodule
