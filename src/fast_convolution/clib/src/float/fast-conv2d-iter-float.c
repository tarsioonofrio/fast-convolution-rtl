#include "lib/include/convolution_float.h"
#include "lib/include/util_float.h"
#include "../../test/test2d/init.h"
#include "../../test/test2d/build_float.h"
#include "../../test/test2d/example_float.h"


main() {
    float ms[A1_SIZE * A2_SIZE] = {0};

    fast_conv_iter_float(ms, ma1t, mc1t, mgg, ma2t, mc2t, md,
                         A1_SIZE, A2_SIZE, C1_SIZE, C2_SIZE);

    print_array1d_float(ms, A1_SIZE * A2_SIZE, "s: ");
    compare_array1d_float_to_int(ms_gold, ms, A1_SIZE * A2_SIZE, "Errors in S != gold");
    return 0;
}

