#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test2d/init.h"
#include "test2d/build.h"
#include "test2d/bind_nest.h"
#include "test2d/example_nest.h"


int main() {
    float mgg2[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    float matf[A_SIZE * C_SIZE] = {0};
    float mctf[C_SIZE * C_SIZE] = {0};
    float mdf[C_SIZE] = {0};

    convert_int_to_float(mat, matf, C_SIZE * A_SIZE);
    convert_int_to_float(mct, mctf, C_SIZE * C_SIZE);
    convert_int_to_float(md, mdf, C_SIZE);

    to_bg(mgg2, mq, mb, mg, B_SIZE, C_SIZE);
    fast_conv1d_float(ms, matf, mgg2, mctf, mdf, A_SIZE, C_SIZE);

    printf("s=S*a: ");
    for (i = 0; i < A_SIZE; i++) {
        printf("%.3f\t", ms[i]);
    };
    printf("\n");



    return 0;
}

