module Transform #(
    parameter int NBITS = 20,
    parameter int A1_SIZE = {a1_size},
    parameter int C1_SIZE = {c1_size},
    parameter int M1_SIZE = {m1_size}
  ) (
    input  logic [NBITS-1:0] pin [C1_SIZE*C1_SIZE-1:0],
    output logic [NBITS-1:0] pout [M1_SIZE*M1_SIZE-1:0]
  );
  timeunit 1ns;
  timeprecision 1ps;

  logic [NBITS-1:0] partial [C1_SIZE*M1_SIZE-1:0];

  // Instance of matrix multiplier "C"
  MatrixC0 #(
    .NBITS(NBITS),
    .C1_SIZE(C1_SIZE),
    .M1_SIZE(M1_SIZE)
  ) matrix_c0(
    .P(pin),
    .soma(partial)
  );
  MatrixC1 #(
    .NBITS(NBITS),
    .C1_SIZE(C1_SIZE),
    .M1_SIZE(M1_SIZE)
  ) matrix_c1(
    .P(partial),
    .soma(pout)
  );
endmodule

module Inverse #(
    parameter int NBITS = 20,
    parameter int A1_SIZE = {a1_size},
    parameter int C1_SIZE = {c1_size},
    parameter int M1_SIZE = {m1_size}
  ) (
    input  logic [NBITS-1:0] pin [M1_SIZE*M1_SIZE-1:0],
    output logic [NBITS-1:0] pout [A1_SIZE*A1_SIZE-1:0]
 );
  timeunit 1ns;
  timeprecision 1ps;

  logic [NBITS-1:0] partial [C1_SIZE*M1_SIZE-1:0];

  MatrixA1 #(
    .NBITS(NBITS),
    .C1_SIZE(C1_SIZE),
    .M1_SIZE(M1_SIZE)
  ) matrix_a1 (
    .P(pin),
    .soma(partial)
  );
  MatrixA0 #(
    .NBITS(NBITS),
    .A1_SIZE(A1_SIZE),
    .C1_SIZE(C1_SIZE),
    .M1_SIZE(M1_SIZE)
  ) matrix_a0 (
    .P(partial),
    .soma(pout)
  );
endmodule
