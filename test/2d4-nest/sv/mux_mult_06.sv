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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; idx[0]=3; idx[0]=4; idx[0]=5; end
      MUL1: begin idx[1]=6; idx[1]=7; idx[1]=8; idx[1]=9; idx[1]=10; idx[1]=11; end
      MUL2: begin idx[2]=12; idx[2]=13; idx[2]=14; idx[2]=15; idx[2]=16; idx[2]=17; end
      MUL3: begin idx[3]=18; idx[3]=19; idx[3]=20; idx[3]=21; idx[3]=22; idx[3]=23; end
      MUL4: begin idx[4]=24; idx[4]=25; idx[4]=26; idx[4]=27; idx[4]=28; idx[4]=29; end
      MUL5: begin idx[5]=30; idx[5]=31; idx[5]=32; idx[5]=33; idx[5]=34; idx[5]=35; end
    default: begin end
    endcase
  end

endmodule
