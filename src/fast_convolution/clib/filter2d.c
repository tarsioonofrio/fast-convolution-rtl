#include "libs/include/convolution.h"
#include "libs/include/util.h"
#include "test2d/init.h"
#include "test2d/bind_nest.h"
#include "test2d/sim.h"

int main() {
    int feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    filter2d_slide2d(feat_out, feat_in, mc_nest, ma_nest, weight_gg_quant,
                     A1_SIZE, C1_SIZE, FIN_SIZE, FOUT_SIZE);

    right_shift_array(feat_out, QUANT_BITS, FOUT_SIZE*FOUT_SIZE);
    print_array2d(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d(gold_quant, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

