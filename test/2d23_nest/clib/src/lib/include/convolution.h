//
// Created by tarsio on 19/06/2024.
//

#ifndef C_CONVOLUTION_H
#define C_CONVOLUTION_H

#define NESTED 0
#define ITERATED 1

typedef struct {
    const int *mgg;
    const int *ma;
    const int *mc;
    const int *ma1;
    const int *ma2;
    const int *mc1;
    const int *mc2;
    int a1_size;
    int a2_size;
    int c1_size;
    int c2_size;
} type_struct_conv;


void simple_convolution(const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col,
                        int out_col);

void matrix_mul(int *out, const int *in1, const int *in2, int row1, int col2_row1, int col2);

void matrix_transpose(int *out, const int *in, int row, int col);

void hadamart_product(int *out, const int *in1, const int *in2, int row);

void init_array(int *array, int size);

void right_shift_array(int *array, int shift, int size);


#endif //C_CONVOLUTION_H