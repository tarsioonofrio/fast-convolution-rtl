//
// Created by tarsio on 01/08/2024.
//

#ifndef C_CONVOLUTION_FLOAT_H
#define C_CONVOLUTION_FLOAT_H

#define NESTED 0
#define ITERATED 1

typedef struct {
    const float *mgg;
    const float *ma;
    const float *mc;
    const float *ma1;
    const float *ma2;
    const float *mc1;
    const float *mc2;
    int a1_size;
    int a2_size;
    int c1_size;
    int c2_size;
} type_struct_conv;



void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2);

void matrix_transpose_float(float *out, const float *in, int row, int col);

void hadamart_product_float(float *out, const float *in1, const float *in2, int row);

void fast_conv_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                     int c_size);

void fast_conv_iter_float(float *ms, const float *ma1t, const float *mc1t, const float *mgg,
                          const float *ma2t, const float *mc2t, const float *md,
                          int a1_size, int a2_size, int c1_size, int c2_size);

void to_bg(float *mgg, const float *mq, const float *mb, const float *mg, int b_size, int c_size);

void filter1d_float(float *feature_out, const float *feature_in, int index, const float *mc, const float *ma,
                    const float *mgg, int a_size, int c_size, int fin_size, int fout_size);

void filter2d(float *feature_out, const float *feature_in, int fin_size, int fout_size, int type_conv, type_struct_conv *params);

void convert_float_to_int(const float *float_array, int *int_array, int length);

void init_array_float(float *array, int size);


#endif //C_CONVOLUTION_FLOAT_H
