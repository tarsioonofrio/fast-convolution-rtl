//
// Created by tarsio on 19/06/2024.
//

#ifndef C_CONVOLUTION_H
#define C_CONVOLUTION_H

void naive_convolution( const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col,
                        int out_col);

void fast_conv(int *ms, const int *ma, const int *mgg, const int *mc, const int *md, int a_size, int c_size);

void filter1d_slide1d(int *feature_out, const int *feature_in, int index, const int *mc, const int *ma,
                      const int *mgg, int a_size, int c_size, int fin_size, int fout_size);

void filter2d_slide2d(int *feature_out, const int *feature_in, const int *mc, const int *ma, const int *mgg,
                      int a_size, int c_size, int fin_size, int fout_size);

void matrix_mul(int *out, const int *in1, const int *in2, int row1, int col2_row1, int col2);

void matrix_transpose(int *out, const int *in, int row, int col);

void hadamart_product(int *out, const int *in1, const int *in2, int row);

#endif //C_CONVOLUTION_H