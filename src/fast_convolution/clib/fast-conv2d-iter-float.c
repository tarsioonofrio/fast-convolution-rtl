#include "libs/convolution.h"
#include "libs/util.h"
#include "test2d/init.h"
#include "test2d/build_float.h"
#include "test2d/example_float.h"


int main() {
    float ms[A1_SIZE * A2_SIZE] = {0};
    float mss[C1_SIZE * C2_SIZE] = {0};
    float mss2[A1_SIZE * C1_SIZE] = {0};
    float mdd[C1_SIZE * C2_SIZE] = {0};
    float ma2[A2_SIZE * C2_SIZE] = {0};
    float mc2[C2_SIZE * C2_SIZE] = {0};
    float md2[C1_SIZE * C2_SIZE] = {0};

    matrix_transpose_float(mc2, mc2t, C1_SIZE, C2_SIZE);
    matrix_transpose_float(ma2, ma2t, A2_SIZE, C2_SIZE);
    matrix_mul_float(md2, md, mc2, C1_SIZE, C2_SIZE, C2_SIZE);
    matrix_mul_float(mdd, mc1t, md2, C1_SIZE, C2_SIZE, C2_SIZE);
    hadamart_product_float(mss, mdd, mgg, C1_SIZE * C2_SIZE);
    matrix_mul_float(mss2, mss, ma2, C1_SIZE, C2_SIZE, A2_SIZE);
    matrix_mul_float(ms, ma1t, mss2, A1_SIZE, C2_SIZE, A2_SIZE);

    print_array1d_float(ms, A1_SIZE * A2_SIZE, "s: ");
    compare_array1d_float_to_int(ms_gold, ms, A1_SIZE * A2_SIZE, "Errors in S != gold");
    return 0;
}

