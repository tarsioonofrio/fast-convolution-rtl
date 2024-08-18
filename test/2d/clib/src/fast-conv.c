#include "convolution.h"
#include "util.h"
#include "init.h"
#include "bind_nest.h"
#include "sim.h"

int main() {
    int feat_out[FOUT_SIZE * FOUT_SIZE] = {0};
    type_struct_conv struct_conv = {weight_gg_quant, ma_nest, mc_nest, 0, 0, 0, 0,
                                    A1_SIZE, A2_SIZE, C1_SIZE, C2_SIZE};

    filter2d(feat_out, feat_in, FIN_SIZE, FOUT_SIZE, NESTED, &struct_conv);
    right_shift_array(feat_out, QUANT_BITS, FOUT_SIZE*FOUT_SIZE);
    print_array2d(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d(gold_quant, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

