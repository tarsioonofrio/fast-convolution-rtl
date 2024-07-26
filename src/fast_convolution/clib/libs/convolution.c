//
// Created by tarsio on 19/06/2024.
//

#include <stdio.h>
#include "convolution.h"
#include "util.h"
#include "../test1d/init.h"


void naive_convolution(
        const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col, int out_col) {
    int fr, fc, wr, wc;
    for (fr = 0; fr < f_row - w_row + 1; fr++) {
        for (fc = 0; fc < f_col - w_col + 1; fc++) {
            for (wr = 0; wr < w_row; wr++) {
                for (wc = 0; wc < w_col; wc++) {
                    output[fr * out_col + fc] = output[fr * out_col + fc] +
                                                feature[(fr + wr) * f_col + (fc + wc)] * weight[wr * w_col + wc];
                }
            }
        }
    }
}

void matrix_mul(int *out, const int *in1, const int *in2, int row1, int col2_row1, int col2) {
    int r, c, t;
    for (r = 0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (t = 0; t < col2_row1; t++) {
                out[r * col2 + c] = out[r * col2 + c] + in1[r * col2_row1 + t] * in2[t * col2 + c];
            }
        }
    }
}

void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2) {
    int r, c, t;
    for (r = 0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (t = 0; t < col2_row1; t++) {
                out[r * col2 + c] = out[r * col2 + c] + in1[r * col2_row1 + t] * in2[t * col2 + c];
            }
        }
    }
}

void hadamart_product(int *out, const int *in1, const int *in2, int row) {
    int r;
    for (r = 0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}

void hadamart_product_float(float *out, const float *in1, const float *in2, int row) {
    int r;
    for (r = 0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}

void fast_conv1d_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                       int c_size) {
    // TODO declare array with malloc/calloc
    float mss[C_SIZE] = {0};
    float mdd[C_SIZE] = {0};
    int i = 0;
    for (i = 0; i < a_size; i++) {
        ms[i] = 0;
    };
    // D=ct*d
    matrix_mul_float(mdd, mc, md, c_size, c_size, 1);
    // S=D.G
    hadamart_product_float(mss, mdd, mgg, c_size);
    // s=S*a
    matrix_mul_float(ms, ma, mss, a_size, c_size, 1);
}

void to_bg(float *mgg, const int *mq, const int *mb, const int *mg, int b_size, int c_size) {
    int i;
    // TODO declare array with malloc/calloc
    float mbg[C_SIZE] = {0};
    float mqf[C_SIZE] = {0};
    float mgf[B_SIZE] = {0};
    float mbf[C_SIZE*B_SIZE] = {0};
    convert_int_to_float(mg, mgf, b_size);
    convert_int_to_float(mb, mbf, c_size*b_size);

    for (i = 0; i < C_SIZE; i++) {
        mqf[i] = (float)mq[i*2] / (float)mq[i*2 + 1];
    }

    // G=q.(b*g)
    // bg=b*g
    matrix_mul_float(mbg, mbf, mgf, c_size, b_size, 1);
    //print_array1d_float(mbg, c_size, "bg=b*g: ");
    // G=q.bg
    hadamart_product_float(mgg, mqf, mbg, c_size);
    //print_array1d_float(mgg, c_size, "G=q.bg: ");
}

void filter1d_slide1d_float(float *feature_out, const int *feature_in, int index, const float *mc, const float *ma,
                            const float *mgg, int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, i;
    // TODO declare array with malloc/calloc
    float md[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    for (r = index; r < fout_size + index; r++) {
        for (c = 0; c <= fout_size; c = c + a_size) {
            for (i = 0; i < c_size; i++) {
                if (c + i < fin_size) {
                    md[i] = (float)feature_in[r * fin_size + c + i];
                } else {
                    md[i] = 0;
                }
            }
            fast_conv1d_float(ms, ma, mgg, mc, md, a_size, c_size);
            for (i = 0; i < a_size; i++) {
                if (c + i < fout_size) {
                    feature_out[(r - index) * fout_size + c + i] += ms[i];
                }
            }
        }
    }
}

void
filter2d_slide2d_float(float *feature_out, const int *feature_in, const float *mc, const float *ma, const float *mgg,
                       int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, rd, cd;
    float md[C_SIZE*C_SIZE] = {0};
    float ms[A_SIZE*A_SIZE] = {0};

    for (r = 0; r < fin_size; r++) {
        for (c = 0; c <= fin_size - a_size; c = c + a_size) {
            for (rd = 0; rd < c_size; rd++) {
                for (cd = 0; cd < c_size; cd++) {
                    if ((r + rd < fin_size) && (c + cd < fin_size) ) {
                        md[rd] = (float)feature_in[r * fin_size + c + rd];
                    } else {
                        md[rd] = 0;
                    }
                }
            }
            fast_conv1d_float(ms, ma, mgg, mc, md, a_size, c_size);
            for (rd = 0; rd < a_size; rd++) {
                if (c + rd < fout_size) {
                    feature_out[r * fout_size + c + rd] = ms[rd];
                }
            }
        }
    }
}