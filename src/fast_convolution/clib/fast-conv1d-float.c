#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/build.h"
#include "test1d/example.h"


int main() {
    int i;

    float mgg2[C_SIZE] = {0};
    float msf[A_SIZE] = {0};
    int ms[A_SIZE] = {0};

    float matf[A_SIZE * C_SIZE] = {0};
    float mctf[C_SIZE * C_SIZE] = {0};
    float mdf[C_SIZE] = {0};

    convert_int_to_float(mat, matf, C_SIZE * A_SIZE);
    convert_int_to_float(mct, mctf, C_SIZE * C_SIZE);
    convert_int_to_float(md, mdf, C_SIZE);

    to_bg(mgg2, mq, mb, mg, B_SIZE, C_SIZE);
    fast_conv_float(msf, matf, mgg2, mctf, mdf, A_SIZE, C_SIZE);

    printf("s=S*a: ");
    for (i = 0; i < A_SIZE; i++) {
        printf("%.3f\t", msf[i]);
    };
    printf("\n");
    convert_float_to_int(msf, ms, A_SIZE);
    compare_array1d(ms_gold, ms, A_SIZE, "Errors:");

    return 0;
}

