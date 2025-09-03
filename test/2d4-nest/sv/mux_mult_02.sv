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
      MUL0: begin idx[0]=0; idx[0]=1; end
      MUL1: begin idx[1]=2; idx[1]=3; end
      MUL2: begin idx[2]=4; idx[2]=5; end
      MUL3: begin idx[3]=6; idx[3]=7; end
      MUL4: begin idx[4]=8; idx[4]=9; end
      MUL5: begin idx[5]=10; idx[5]=11; end
      MUL6: begin idx[6]=12; idx[6]=13; end
      MUL7: begin idx[7]=14; idx[7]=15; end
      MUL8: begin idx[8]=16; idx[8]=17; end
      MUL9: begin idx[9]=18; idx[9]=19; end
      MUL10: begin idx[10]=20; idx[10]=21; end
      MUL11: begin idx[11]=22; idx[11]=23; end
      MUL12: begin idx[12]=24; idx[12]=25; end
      MUL13: begin idx[13]=26; idx[13]=27; end
      MUL14: begin idx[14]=28; idx[14]=29; end
      MUL15: begin idx[15]=30; idx[15]=31; end
      MUL16: begin idx[16]=32; idx[16]=33; end
      MUL17: begin idx[17]=34; idx[17]=35; end
    default: begin end
    endcase
  end

endmodule
