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
      MUL4: begin idx[4]=16; idx[4]=17; idx[4]=18; idx[4]=19; end
      MUL5: begin idx[5]=20; idx[5]=21; idx[5]=22; idx[5]=23; end
      MUL6: begin idx[6]=24; idx[6]=25; idx[6]=26; idx[6]=27; end
      MUL7: begin idx[7]=28; idx[7]=29; idx[7]=30; idx[7]=31; end
      MUL8: begin idx[8]=32; idx[8]=33; idx[8]=34; idx[8]=35; end
    default: begin end
    endcase
  end

endmodule
