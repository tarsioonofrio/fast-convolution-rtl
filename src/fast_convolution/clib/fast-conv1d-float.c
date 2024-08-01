#include <stdio.h>
#include "libs/include/convolution_float.h"
#include "libs/include/util_float.h"
#include "test1d/init.h"
#include "test1d/build_float.h"
#include "test1d/example_float.h"


int main() {
    float mgg2[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    to_bg(mgg2, mq, mb, mg, B_SIZE, C_SIZE);
    print_array1d_float(mgg2, C_SIZE, "G: ");
    fast_conv_float(ms, mat, mgg2, mct, md, A_SIZE, C_SIZE);

    print_array1d_float(ms, A_SIZE, "s: ");
    compare_array1d_float_to_int(ms_gold, ms, A_SIZE, "Errors:");

    return 0;
}

