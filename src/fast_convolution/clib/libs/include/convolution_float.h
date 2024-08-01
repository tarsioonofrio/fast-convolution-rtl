//
// Created by tarsio on 01/08/2024.
//

#ifndef C_CONVOLUTION_FLOAT_H
#define C_CONVOLUTION_FLOAT_H

void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2);

void matrix_transpose_float(float *out, const float *in, int row, int col);

void hadamart_product_float(float *out, const float *in1, const float *in2, int row);

void fast_conv_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                     int c_size);

void to_bg(float *mgg, const float *mq, const float *mb, const float *mg, int b_size, int c_size);

void filter1d_slide1d_float(float *feature_out, const float *feature_in, int index, const float *mc, const float *ma,
                       const float *mgg, int a_size, int c_size, int fin_size, int fout_size);

void filter2d_slide2d_float(float *feature_out, const float *feature_in, const float *mc, const float *ma, const float *mgg,
                       int a_size, int c_size, int fin_size, int fout_size);

#endif //C_CONVOLUTION_FLOAT_H
