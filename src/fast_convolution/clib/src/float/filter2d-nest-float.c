#include "convolution_float.h"
#include "util_float.h"
#include "init.h"
#include "build_float.h"
#include "sim_float.h"

int main() {
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};
    type_struct_conv struct_conv = {weight_gg, 0, 0, ma1t, ma2t, mc1t, mc2t,
                                    A1_SIZE, A2_SIZE, C1_SIZE, C2_SIZE, M1_SIZE, M2_SIZE};

    filter2d(feat_out, feat_in, FIN_SIZE, FOUT_SIZE, NEST, &struct_conv);
    print_array2d_float(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d_float_to_int(gold, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

