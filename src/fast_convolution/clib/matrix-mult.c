#include <stdio.h>
#include "libs/convolution.h"
#include "test1d/sim.h"

int main() {
    const int m2[4 * 4] = {
            -1, 0, 0, 0,
            0, -1, 1, -1,
            1, 1, 1, 0,
            0, 0, 0, 1
    };

    int m3[4 * 4] = {0};

    int row1 = 4, col1 = 4, row2 = 4, col2 = 4, row3 = 4, col3 = 4;
    int r;
    int c;
    matrix_mul(m3, feature_fast_4_4, m2, row1, col1, col2);

    for (r = 0; r < row3; r++) {
        for (c = 0; c < col3; c++) {
            printf("%d\t", m3[r * col3 + c]);
        }
        printf("\n");
    }

    return 0;
}

