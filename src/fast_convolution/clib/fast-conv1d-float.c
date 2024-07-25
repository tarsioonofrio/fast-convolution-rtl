#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/build.h"
#include "test1d/example.h"


int main() {
    int i;

    float mgg[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    float matf[A_SIZE * C_SIZE] = {0};
    float mctf[C_SIZE * C_SIZE] = {0};
    float mdf[C_SIZE] = {0};

    convert_int_to_float(mat, matf, C_SIZE * A_SIZE);
    convert_int_to_float(mct, mctf, C_SIZE * C_SIZE);
    convert_int_to_float(md, mdf, C_SIZE);

    to_bg(mgg, mq, mb, mg, B_SIZE, C_SIZE);
    fast_conv1d_float(ms, matf, mgg, mctf, mdf, A_SIZE, C_SIZE);

    printf("s=S*a: ");
    for (i = 0; i < A_SIZE; i++) {
        printf("%.3f\t", ms[i]);
    };
    printf("\n");

    return 0;
}

