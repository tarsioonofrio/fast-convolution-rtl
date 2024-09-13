//
// Created by tarsio on 19/06/2024.
//

#include <stdlib.h>
#include "convolution.h"
#include "fast_conv.h"

#ifdef __riscv
    #include <riscv-csr.h>
#endif


void simple_convolution(
        const int *weight, const int *feature, int *output, int f_row, int f_col, int w_row, int w_col, int out_col) {
    int fr, fc, wr, wc;

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif

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
    #ifdef __riscv
        csr_write_mcountinhibit(-1);
    #endif
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


void filter1d(int *feature_out, const int *feature_in, int index, const int *mc, const int *ma,
              const int *mgg, int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, i;
    int *ms = (int *) malloc((a_size) * sizeof(int));
    int *md = (int *) malloc((c_size) * sizeof(int));

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif

    for (r = index; r < fout_size + index; r++) {
        for (c = 0; c <= fout_size; c = c + a_size) {
            for (i = 0; i < c_size; i++) {
                if (c + i < fin_size) {
                    md[i] = feature_in[r * fin_size + c + i];
                } else {
                    md[i] = 0;
                }
            }
            fast_conv(ms, ma, mgg, mc, md, a_size, c_size);
            for (i = 0; i < a_size; i++) {
                if (c + i < fout_size) {
                    feature_out[(r - index) * fout_size + c + i] += ms[i];
                }
            }
        }
    }

    #ifdef __riscv
        csr_write_mcountinhibit(-1);
    #endif

    free(ms);
    free(md);
}


void filter2d(int *feature_out, const int *feature_in, int fin_size, int fout_size, int type_conv,
              type_struct_conv *params) {
    int r, c, rd, cd;
    int a1_size = params->a1_size;
    int a2_size = params->a2_size;
    int c1_size = params->c1_size;
    int c2_size = params->c2_size;
    int *ms = (int *) malloc((a1_size * a1_size) * sizeof(int));
    int *md = (int *) malloc((c1_size * c1_size) * sizeof(int));

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif

    for (r = 0; r < fout_size; r = r + a1_size) {
        for (c = 0; c <= fout_size; c = c + a2_size) {
            for (rd = 0; rd < c1_size; rd++) {
                for (cd = 0; cd < c2_size; cd++) {
                    if ((r + rd < fin_size) && (c + cd < fin_size)) {
                        md[rd * c1_size + cd] = feature_in[r * fin_size + rd * fin_size + c + cd];
                    } else {
                        md[rd * c1_size + cd] = 0;
                    }
                }
            }
            if (type_conv == NESTED) {
                fast_conv(ms, params->ma, params->mgg, params->mc, md,
                          a1_size * a2_size, c1_size * c2_size);
            } else if (type_conv == ITERATED) {
                fast_conv_iter(ms, params->ma1, params->mc1, params->mgg, params->ma2, params->mc2, md,
                               a1_size, a2_size, c1_size, c2_size);
            }
            for (rd = 0; rd < a1_size; rd++) {
                for (cd = 0; cd < a2_size; cd++) {
                    if (c + rd < fout_size) {
                        feature_out[r * fout_size + rd * fout_size + c + cd] = ms[rd * a1_size + cd];
                    }
                }
            }
        }
    }

    #ifdef __riscv
        csr_write_mcountinhibit(-1);
    #endif

    free(ms);
    free(md);
}

void init_array(int *array, int size) {
    int i;
    for (i = 0; i < size; i++) {
        array[i] = 0;
    };
}

void right_shift_array(int *array, int shift, int size) {
    int i;

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif

    for (i = 0; i < size; i++) {
        array[i] = array[i] >> shift;
    };

    #ifdef __riscv
        csr_write_mcountinhibit(-1);
    #endif
}
