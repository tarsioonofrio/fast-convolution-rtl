#include <stdio.h>

void naive_convolution(const int *weight, const int *feature, int *output, int f_row, int f_col, int g_col, int w_row, int w_col);

int main() {

    int weight[3 * 3] = {
            1, 0, 1,
            2, 1, 2,
            1, 2, 1
    };
    int feature[8 * 8] = {
             0,  1,  2,  3,  4,  5,  6,  7,
             8,  9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23,
            24, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 34, 35, 36, 37, 38, 39,
            40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 53, 54, 55,
            56, 57, 58, 59, 60, 61, 62, 63
    };
    int gold[6 * 6] = {
            115, 126, 137, 148, 159, 170,
            203, 214, 225, 236, 247, 258,
            291, 302, 313, 324, 335, 346,
            379, 390, 401, 412, 423, 434,
            467, 478, 489, 500, 511, 522,
            555, 566, 577, 588, 599, 610
    };
    int output[6 * 6] = {0};
    int f_row=8, f_col=8, g_row=6, g_col=6, w_row=3, w_col=3;
    int gi, gj;

    naive_convolution(weight, feature, output, f_row, f_col, g_col, w_row, w_col);

    for (gi=0; gi < g_row; gi++){
        for (gj=0; gj < g_col; gj++){
            printf("%d\t", gold[gi * g_col + gj]);
            if (gold[gi * g_col + gj] != output[gi * g_col + gj]){
                printf("Err %d %d\n", gi, gj);
            }
        }
        printf("\n");
    }

    return 0;
}

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
