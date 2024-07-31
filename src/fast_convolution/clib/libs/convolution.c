//
// Created by tarsio on 19/06/2024.
//

#include <stdio.h>
#include <stdlib.h>
#include "convolution.h"
#include "util.h"
//#include "../test1d/init.h"
//#include "../test2d/init.h"


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
    int r, c, k;
    for (r = 0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (k = 0; k < col2_row1; k++) {
                out[r * col2 + c] += in1[r * col2_row1 + k] * in2[k * col2 + c];
            }
        }
    }
}

void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2) {
    int r, c, k;
    for (r = 0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (k = 0; k < col2_row1; k++) {
                out[r * col2 + c] += in1[r * col2_row1 + k] * in2[k * col2 + c];
            }
        }
    }
}

void matrix_transpose_float(float *out, const float *in, int row, int col) {
    int r, c;
    for (r = 0; r < row; r++) {
        for (c = 0; c < col; c++) {
            out[c * row + r] = in[r * col + c];
        }
    }
}

void matrix_transpose(int *out, const int *in, int row, int col) {
    int r, c;
    for (r = 0; r < row; r++) {
        for (c = 0; c < col; c++) {
            out[c * row + r] = in[r * col + c];
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

void fast_conv_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                     int c_size) {
    float * mss = (float*)malloc((c_size) * sizeof(float));
    float * mdd = (float*)malloc((c_size) * sizeof(float));

    init_array(mss, c_size);
    init_array(mdd, c_size);
    init_array(ms, a_size);

    // D=ct*d
    matrix_mul_float(mdd, mc, md, c_size, c_size, 1);
    // S=D.G
    hadamart_product_float(mss, mdd, mgg, c_size);
    // s=S*a
    matrix_mul_float(ms, ma, mss, a_size, c_size, 1);
    free(mss);
    free(mdd);
}

void to_bg(float *mgg, const float *mq, const float *mb, const float *mg, int b_size, int c_size) {
    int i;
    float * mbg = (float*)malloc((c_size) * sizeof(float));
    float * mqf = (float*)malloc((c_size) * sizeof(float));
    init_array(mbg, c_size);
    init_array(mqf, c_size);

    for (i = 0; i < c_size; i++) {
        mqf[i] = mq[i*2] / mq[i*2 + 1];
    }
    // G=q.(b*g)
    // bg=b*g
    matrix_mul_float(mbg, mb, mg, c_size, b_size, 1);
    //print_array1d_float(mbg, c_size, "bg=b*g: ");
    // G=q.bg
    hadamart_product_float(mgg, mqf, mbg, c_size);
    //print_array1d_float(mgg, c_size, "G=q.bg: ");
    free(mbg);
    free(mqf);
}

void filter1d_slide1d_float(float *feature_out, const float *feature_in, int index, const float *mc, const float *ma,
                            const float *mgg, int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, i;
    float * ms = (float*)malloc((a_size) * sizeof(float));
    float * md = (float*)malloc((c_size) * sizeof(float));

    for (r = index; r < fout_size + index; r++) {
        for (c = 0; c <= fout_size; c = c + a_size) {
            for (i = 0; i < c_size; i++) {
                if (c + i < fin_size) {
                    md[i] = feature_in[r * fin_size + c + i];
                } else {
                    md[i] = 0;
                }
            }
            fast_conv_float(ms, ma, mgg, mc, md, a_size, c_size);
            for (i = 0; i < a_size; i++) {
                if (c + i < fout_size) {
                    feature_out[(r - index) * fout_size + c + i] += ms[i];
                }
            }
        }
    }
    free(ms);
    free(md);
}

void
filter2d_slide2d_float(float *feature_out, const float *feature_in, const float *mc, const float *ma, const float *mgg,
                       int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, rd, cd;
//    float * ms = (float*)malloc((a_size) * sizeof(float));
//    float * md = (float*)malloc((c_size) * sizeof(float));
    float ms[9] = {0};
    float md[25] = {0};
    float tmp = 0;

    for (r = 0; r < fout_size; r = r + a_size) {
        for (c = 0; c <= fout_size; c = c + a_size) {
            for (rd = 0; rd < c_size; rd++) {
                for (cd = 0; cd < c_size; cd++) {
                    if ((r + rd < fin_size) && (c + cd < fin_size) ) {
//                        md[rd] = feature_in[r * fin_size + rd*fin_size + c + cd];
                        tmp = feature_in[r * fin_size + rd * fin_size + c + cd];
                        md[rd*c_size + cd] = tmp;
                    } else {
                        md[rd*c_size + cd] = 0;
                    }
                }
            }
            fast_conv_float(ms, ma, mgg, mc, md, a_size * a_size, c_size * c_size);
            for (rd = 0; rd < a_size; rd++) {
                for (cd = 0; cd < a_size; cd++) {
                    if (c + rd < fout_size) {
                        feature_out[r * fout_size + rd * fout_size + c + cd] = ms[rd * a_size + cd];
                    }
                }
            }
        }
    }
//    free(ms);
//    free(md);
}