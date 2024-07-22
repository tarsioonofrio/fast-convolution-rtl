#include <stdio.h>
#include "libs/convolution.h"
#include "test1d/sim.h"

int main() {
    int output[6 * 6] = {0};
    int f_row = 8, f_col = 8, g_row = 6, g_col = 6, w_row = 3, w_col = 3;
    int gi, gj;

    naive_convolution(weight, feature_in, output, f_row, f_col, w_row, w_col, g_col);

    for (gi = 0; gi < g_row; gi++) {
        for (gj = 0; gj < g_col; gj++) {
            printf("%d\t", gold_gold[gi * g_col + gj]);
            if (gold_gold[gi * g_col + gj] != output[gi * g_col + gj]) {
                printf("Err %d %d\n", gi, gj);
            }
        }
        printf("\n");
    }

    return 0;
}

