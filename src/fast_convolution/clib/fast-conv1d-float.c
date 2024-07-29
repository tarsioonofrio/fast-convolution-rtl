#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/build_float.h"
#include "test1d/example_float.h"


int main() {
    float mgg2[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    to_bg(mgg2, mq, mb, mg, B_SIZE, C_SIZE);
    print_array2d_float(mgg2, 5, 5, "G: ");
    fast_conv_float(ms, mat, mgg2, mct, md, A_SIZE, C_SIZE);

    print_array1d_float(ms, A_SIZE, "s: ");
    compare_array1d_float(ms_gold, ms, A_SIZE, "Errors:");

    return 0;
}

