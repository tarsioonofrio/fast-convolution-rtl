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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; idx[0]=5; idx[0]=6; idx[0]=7; idx[0]=8; end
      MUL1: begin idx[1]=9; idx[1]=10; idx[1]=11; idx[1]=12; idx[1]=13; idx[1]=14; idx[1]=15; idx[1]=16; idx[1]=17; end
      MUL2: begin idx[2]=18; idx[2]=19; idx[2]=20; idx[2]=21; idx[2]=22; idx[2]=23; idx[2]=24; idx[2]=25; idx[2]=26; end
      MUL3: begin idx[3]=27; idx[3]=28; idx[3]=29; idx[3]=30; idx[3]=31; idx[3]=32; idx[3]=33; idx[3]=34; idx[3]=35; end
    default: begin end
    endcase
  end

endmodule
