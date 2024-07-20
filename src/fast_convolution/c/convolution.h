//
// Created by tarsio on 19/06/2024.
//

#ifndef C_CONVOLUTION_H
#define C_CONVOLUTION_H

void naive_convolution(const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col,
                       int out_col);

void matrix_mul(const int *in1, const int *in2, int *out, int row1, int col2_row1, int col2);

#endif //C_CONVOLUTION_H
