#include "libs/include/convolution_float.h"
#include "libs/include/util_float.h"
#include "test2d/init.h"
#include "test2d/bind_nest_float.h"
#include "test2d/sim_float.h"

int main() {
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};
    type_struct_conv struct_conv = {weight_gg, ma_nest, mc_nest, 0, 0, 0, 0,
                                     A1_SIZE, A2_SIZE, C1_SIZE, C2_SIZE};

    filter2d(feat_out, feat_in, FIN_SIZE, FOUT_SIZE, NESTED, &struct_conv);
    print_array2d_float(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d_float_to_int(gold, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

