#include "convolution_float.h"
#include "util_float.h"
#include "init.h"
#include "build_float.h"
#include "example_float.h"


int main() {
    float mgg2[6] = {0};
    float ms[A_SIZE] = {0};

    to_bg(mgg2, mq, mb, mg, B_SIZE, M_SIZE);
    print_array1d_float(mgg2, M_SIZE, "G: ");
    fast_conv_float(ms, mat, mgg2, mct, md, A_SIZE, C_SIZE, M_SIZE);

    print_array1d_float(ms, A_SIZE, "s: ");
    compare_array1d_float_to_int(ms_gold, ms, A_SIZE, "Errors:");

    return 0;
}

