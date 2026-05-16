module Transform #(
    parameter int NBITS = 20,
    parameter int TRANSFORM_SIZE = {a1_size},
    parameter int B_SIZE = {a1_size},
    parameter int INVERSE_SIZE = {c1_size},
    parameter int HADAMARD_SIZE = {m1_size}
  ) (
    input  logic [NBITS-1:0] pin [INVERSE_SIZE*INVERSE_SIZE-1:0],
    output logic [NBITS-1:0] pout [HADAMARD_SIZE*HADAMARD_SIZE-1:0]
  );
  timeunit 1ns;
  timeprecision 1ps;

  logic [NBITS-1:0] partial [INVERSE_SIZE*HADAMARD_SIZE-1:0];

  // Instance of matrix multiplier "C"
  MatrixC0 #(
    .NBITS(NBITS),
    .INVERSE_SIZE(INVERSE_SIZE),
    .HADAMARD_SIZE(HADAMARD_SIZE)
  ) matrix_c0(
    .P(pin),
    .soma(partial)
  );
  MatrixC1 #(
    .NBITS(NBITS),
    .INVERSE_SIZE(INVERSE_SIZE),
    .HADAMARD_SIZE(HADAMARD_SIZE)
  ) matrix_c1(
    .P(partial),
    .soma(pout)
  );
endmodule

module Inverse #(
    parameter int NBITS = 20,
    parameter int TRANSFORM_SIZE = {a1_size},
    parameter int B_SIZE = {a1_size},
    parameter int INVERSE_SIZE = {c1_size},
    parameter int HADAMARD_SIZE = {m1_size}
  ) (
    input  logic [NBITS-1:0] pin [HADAMARD_SIZE*HADAMARD_SIZE-1:0],
    output logic [NBITS-1:0] pout [TRANSFORM_SIZE*TRANSFORM_SIZE-1:0]
 );
  timeunit 1ns;
  timeprecision 1ps;

  logic [NBITS-1:0] partial [INVERSE_SIZE*HADAMARD_SIZE-1:0];

  MatrixA1 #(
    .NBITS(NBITS),
    .INVERSE_SIZE(INVERSE_SIZE),
    .HADAMARD_SIZE(HADAMARD_SIZE)
  ) matrix_a1 (
    .P(pin),
    .soma(partial)
  );
  MatrixA0 #(
    .NBITS(NBITS),
    .TRANSFORM_SIZE(TRANSFORM_SIZE),
    .INVERSE_SIZE(INVERSE_SIZE),
    .HADAMARD_SIZE(HADAMARD_SIZE)
  ) matrix_a0 (
    .P(partial),
    .soma(pout)
  );
endmodule
