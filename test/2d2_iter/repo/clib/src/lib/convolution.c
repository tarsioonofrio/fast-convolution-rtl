//
// Created by tarsio on 19/06/2024.
//

#include <stdlib.h>
#include "convolution.h"
#include "fast_conv.h"
#include "filter1dim.h"

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
