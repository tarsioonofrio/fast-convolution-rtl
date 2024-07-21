//
// Created by tarsio on 19/06/2024.
//

#ifndef C_CONVOLUTION_H
#define C_CONVOLUTION_H

void naive_convolution(
        const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col, int out_col
);

void fast_conv1d_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                       int c_size);

void filter1d_slide1d(float *feature_out, const float *feature_in, const float *mc, const float *ma, float *md,
                      const float *mgg,
                      float *ms, int a_size, int c_size);

void to_bg(float *mgg, const float *mq, const float *mb, const float *mg, int b_size, int c_size);


void matrix_mul(int *out, const int *in1, const int *in2, int row1, int col2_row1, int col2);

void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2);

void hadamart_product(int *out, const int *in1, const int *in2, int row);

void hadamart_product_float(float *out, const float *in1, const float *in2, int row);


#endif //C_CONVOLUTION_H