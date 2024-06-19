#include <stdio.h>
#include "convolution.h"
#include "example.h"

int main() {
    const int m2[4*4] = {
        -1, 0, 0, 0,
        0, -1, 1, -1,
        1, 1, 1, 0,
        0, 0, 0, 1
    };

    int m3[4 * 4] = {0};

    int row1=4, col1=4, row2=4, col2=4, row3=4, col3=4;
    int r;
    int c;
    matrix_mul(feature_fast_4_4, m2, m3, row1, col2, col1);

    for (r=0; r < row3; r++) {
        for (c = 0; c < col3; c++) {
            printf("%d\t", m3[r*col3 + c]);
        }
        printf("\n");
    }

    int output[6 * 6] = {0};
    int f_row=8, f_col=8, g_row=6, g_col=6, w_row=3, w_col=3;
    int gi, gj;

    naive_convolution(weight_3_3, feature_8_8, output, f_row, f_col, w_row, w_col, g_col);

    for (gi=0; gi < g_row; gi++){
        for (gj=0; gj < g_col; gj++){
            printf("%d\t", gold_6_6[gi * g_col + gj]);
            if (gold_6_6[gi * g_col + gj] != output[gi * g_col + gj]){
                printf("Err %d %d\n", gi, gj);
            }
        }
        printf("\n");
    }

    return 0;
}

