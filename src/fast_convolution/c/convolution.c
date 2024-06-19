//
// Created by tarsio on 19/06/2024.
//

#include <stdio.h>
#include "convolution.h"


void naive_convolution(const int *weight, const int *feature, int *output, int f_row, int f_col, int g_col, int w_row, int w_col) {
    int fi, fj, wi, wj;
    for (fi=0; fi < f_row - w_row + 1; fi++){
        for (fj=0; fj < f_col - w_col + 1; fj++){
            for (wi=0; wi < w_row; wi++){
                for (wj=0; wj < w_col; wj++){
                    output[fi * g_col + fj] = output[fi * g_col + fj] + feature[(fi + wi) * f_col + (fj + wj)] * weight[wi * w_col + wj];
                }
            }
        }
    }
}