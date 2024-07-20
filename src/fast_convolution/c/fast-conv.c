#include <stdio.h>
#include "convolution.h"
#include "example.h"

#define A_SIZE 3
#define B_SIZE 3
#define C_SIZE 5

int main() {
    const int m2[4*4] = {
        -1, 0, 0, 0,
        0, -1, 1, -1,
        1, 1, 1, 0,
        0, 0, 0, 1
    };
    const int mc[5*5] = {
        2, -1,-2, 1,0,
        0, -2, -1, 1, 0,
        0, 2, -3, 1, 0,
        0, -1, 0, 1, 0,
        0, 2, -1, -2, 1,
    };

    const int mb[5*3] = {
            1, 0, 0,
            1, 1, 1,
            1, -1, 1,
            1, 2, 4,
            0, 0, 1,
    };

    int md[C_SIZE] = {0, 1, 2, 3, 4};
    int mg[B_SIZE] = {0, 1, 2};
    float mq[C_SIZE] = {1/2, -1/2, -1/6, 1/6, 1};
    int mdd[C_SIZE] = {0};
    int mgg[C_SIZE] = {0};
    int ms[A_SIZE] = {0};

    int r;
    int c;
    matrix_mul(mc, md, mdd, C_SIZE, C_SIZE, 1);

    for (r=0; r < C_SIZE; r++) {
        printf("%d\t", mdd[r]);
    }

    return 0;
}

