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
      MUL0: begin idx[0]=0; idx[0]=1; idx[0]=2; end
      MUL1: begin idx[1]=3; idx[1]=4; idx[1]=5; end
      MUL2: begin idx[2]=6; idx[2]=7; idx[2]=8; end
      MUL3: begin idx[3]=9; idx[3]=10; idx[3]=11; end
      MUL4: begin idx[4]=12; idx[4]=13; idx[4]=14; end
      MUL5: begin idx[5]=15; idx[5]=16; idx[5]=17; end
      MUL6: begin idx[6]=18; idx[6]=19; idx[6]=20; end
      MUL7: begin idx[7]=21; idx[7]=22; idx[7]=23; end
      MUL8: begin idx[8]=24; idx[8]=25; idx[8]=26; end
      MUL9: begin idx[9]=27; idx[9]=28; idx[9]=29; end
      MUL10: begin idx[10]=30; idx[10]=31; idx[10]=32; end
      MUL11: begin idx[11]=33; idx[11]=34; idx[11]=35; end
    default: begin end
    endcase
  end

endmodule
