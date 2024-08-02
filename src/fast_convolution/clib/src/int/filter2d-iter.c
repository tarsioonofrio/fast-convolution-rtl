#include "lib/include/convolution.h"
#include "lib/include/util.h"
#include "../../test/test2d/init.h"
#include "../../test/test2d/build.h"
#include "../../test/test2d/sim.h"

int main() {
    int feat_out[FOUT_SIZE * FOUT_SIZE] = {0};
    type_struct_conv struct_conv = {weight_gg_quant, 0, 0, ma1t, ma2t, mc1t, mc2t,
                                    A1_SIZE, A2_SIZE, C1_SIZE, C2_SIZE};

    filter2d(feat_out, feat_in, FIN_SIZE, FOUT_SIZE, ITERATED, &struct_conv);
    right_shift_array(feat_out, QUANT_BITS, FOUT_SIZE*FOUT_SIZE);
    print_array2d(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d(gold_quant, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

