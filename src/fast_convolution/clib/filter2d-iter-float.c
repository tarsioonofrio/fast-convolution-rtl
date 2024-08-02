#include "libs/include/convolution_float.h"
#include "libs/include/util_float.h"
#include "test2d/init.h"
#include "test2d/build_float.h"
#include "test2d/sim_float.h"

int main() {
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};
    type_struct_conv struct_conv = {weight_gg, 0, 0, ma1t, ma2t, mc1t, mc2t,
                                    A1_SIZE, A2_SIZE, C1_SIZE, C2_SIZE};

    filter2d(feat_out, feat_in, FIN_SIZE, FOUT_SIZE, ITERATED, &struct_conv);
    print_array2d_float(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d_float_to_int(gold, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

