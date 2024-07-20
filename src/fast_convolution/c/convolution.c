//
// Created by tarsio on 19/06/2024.
//

#include "convolution.h"

void naive_convolution(
        const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col,int out_col) {
    int fi, fj, wi, wj;
    for (fi=0; fi < f_row - w_row + 1; fi++){
        for (fj=0; fj < f_col - w_col + 1; fj++){
            for (wi=0; wi < w_row; wi++){
                for (wj=0; wj < w_col; wj++){
                    output[fi * out_col + fj] = output[fi * out_col + fj] + feature[(fi + wi) * f_col + (fj + wj)] * weight[wi * w_col + wj];
                }
            }
        }
    }
}

void matrix_mul_int(const int *in1, const int *in2, int *out, int row1, int col2_row1, int col2) {
    int r, c, t;
    for (r=0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (t = 0; t < col2_row1; t++) {
                out[r * col2 + c] = out[r * col2 + c] + in1[r * col2_row1 + t] * in2[t * col2 + c];
            }
        }
    }
}

void matrix_mul_float(const float *in1, const float *in2, float *out, int row1, int col2_row1, int col2) {
    int r, c, t;
    for (r=0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (t = 0; t < col2_row1; t++) {
                out[r * col2 + c] = out[r * col2 + c] + in1[r * col2_row1 + t] * in2[t * col2 + c];
            }
        }
    }
}

void hadamart_product_int(const int *in1, const int *in2, int *out, int row) {
    int r;
    for (r=0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}

void hadamart_product_float(const float *in1, const float *in2, float *out, int row) {
    int r;
    for (r=0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}