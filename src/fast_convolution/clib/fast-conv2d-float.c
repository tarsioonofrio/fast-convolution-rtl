#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test2d/init.h"
#include "test2d/build.h"
#include "test2d/bind_nest.h"
#include "test2d/example_nest.h"


int main() {
//    float mgg2[C2_SIZE * C2_SIZE] = {0};
    int i;
    float ms[A1_SIZE * A2_SIZE] = {0};

    float manf[A1_SIZE * A2_SIZE * C1_SIZE * C2_SIZE] = {0};
    float mcnf[C1_SIZE * C1_SIZE * C2_SIZE * C2_SIZE] = {0};
    float mdf[C1_SIZE * C2_SIZE] = {0};

    convert_int_to_float(ma_nest, manf, A1_SIZE * A2_SIZE * C1_SIZE * C2_SIZE);
    convert_int_to_float(mc_nest, mcnf, C1_SIZE * C1_SIZE * C2_SIZE * C2_SIZE);
    convert_int_to_float(md, mdf, C1_SIZE * C2_SIZE);

//    to_bg(mgg2, mq, mb, mg, B_SIZE, C_SIZE);
    fast_conv1d_float(ms, manf, mggf, mcnf, mdf, A1_SIZE * A2_SIZE, C1_SIZE * C2_SIZE);

    printf("s=S*a: ");
    for (i = 0; i < A1_SIZE * A2_SIZE; i++) {
        printf("%.3f\t", ms[i]);
    };
    printf("\n");

    compare_array1d(ms_gold, ms, A1_SIZE * A2_SIZE, "Errors in S != gold");



    return 0;
}

