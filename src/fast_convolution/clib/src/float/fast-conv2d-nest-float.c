#include "convolution_float.h"
#include "util_float.h"
#include "init.h"
#include "bind_nest_float.h"
#include "example_float.h"

int main() {
    float ms[A1_SIZE * A2_SIZE] = {0};

    fast_conv_float(ms, ma_nest, mgg, mc_nest, md, A1_SIZE * A2_SIZE, C1_SIZE * C2_SIZE);

    print_array1d_float(ms, A1_SIZE * A2_SIZE, "s: ");
    compare_array1d_float_to_int(ms_gold, ms, A1_SIZE * A2_SIZE, "Errors in S != gold");
    return 0;
}

