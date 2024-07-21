//
// Created by tarsio on 19/06/2024.
//

#include "example.h"
#include <stdio.h>
#include "convolution.h"
#include "config.h"
#include "util.h"


void naive_convolution(
        const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col,int out_col) {
    int fr, fc, wr, wc;
    for (fr=0; fr < f_row - w_row + 1; fr++){
        for (fc=0; fc < f_col - w_col + 1; fc++){
            for (wr=0; wr < w_row; wr++){
                for (wc=0; wc < w_col; wc++){
                    output[fr * out_col + fc] = output[fr * out_col + fc] + feature[(fr + wr) * f_col + (fc + wc)] * weight[wr * w_col + wc];
                }
            }
        }
    }
}

void matrix_mul(int *out, const int *in1, const int *in2, int row1, int col2_row1, int col2) {
    int r, c, t;
    for (r=0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (t = 0; t < col2_row1; t++) {
                out[r * col2 + c] = out[r * col2 + c] + in1[r * col2_row1 + t] * in2[t * col2 + c];
            }
        }
    }
}

void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2) {
    int r, c, t;
    for (r=0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (t = 0; t < col2_row1; t++) {
                out[r * col2 + c] = out[r * col2 + c] + in1[r * col2_row1 + t] * in2[t * col2 + c];
            }
        }
    }
}

void hadamart_product(int *out, const int *in1, const int *in2, int row) {
    int r;
    for (r=0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}

void hadamart_product_float(float *out, const float *in1, const float *in2, int row) {
    int r;
    for (r=0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}

void fast_conv1d_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                       int c_size) {
    float mss[C_SIZE] = {0};
    float mdd[C_SIZE] = {0};
    int i = 0;
    for (i = 0; i < A_SIZE; i++) {
        ms[i] = 0;
    };
    // D=ct*d
    matrix_mul_float(mdd, mc, md, c_size, c_size, 1);
    // S=D.G
    hadamart_product_float(mss, mdd, mgg, c_size);
    // s=S*a
    matrix_mul_float(ms, ma, mss, a_size, c_size, 1);
}

void
to_bg(float *mgg, const float *mq, const float *mb, const float *mg, int b_size, int c_size) {
    float mbg[C_SIZE] = {0};
    // G=q.(b*g)
    // bg=b*g
    matrix_mul_float(mbg, mb, mg, c_size, b_size, 1);
    //print_array1d_float(mbg, c_size, "bg=b*g: ");
    // G=q.bg
    hadamart_product_float(mgg, mq, mbg, c_size);
    //print_array1d_float(mgg, c_size, "G=q.bg: ");
}

void filter1d_slide1d(
        float *feature_out, const float *feature_in, const float *mc, const float *ma, float *md, const float *mgg,
        float *ms, int a_size, int c_size) {
    int r, c, i;
    for (r=0; r < FIN_SIZE; r++) {
        for (c=0; c <= FIN_SIZE - A_SIZE; c=c+A_SIZE) {
            for (i = 0; i < C_SIZE; i++) {
                if (c + i < FIN_SIZE) {
                    md[i] = feature_in[r * FIN_SIZE + c + i];
                }
                else {
                    md[i] = 0;
                }
            }
            fast_conv1d_float(ms, ma, mgg, mc, md, a_size, c_size);
            for (i = 0; i < C_SIZE; i++) {
                if (c + i < FOUT_SIZE) {
                    feature_out[r * FOUT_SIZE + c + i] = ms[i];
                }
                else {
                    feature_out[r * FOUT_SIZE + c + i] = ms[i];
                }
            }
        }
    }
}