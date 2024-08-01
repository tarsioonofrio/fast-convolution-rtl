#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/build.h"
#include "test1d/sim.h"

int main() {
    int i;
    const int *mgg;
    int feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    for (i=0; i < W_SIZE; i++) {
        mgg = weight_gg_quant + C_SIZE*C_SIZE*i;
        filter1d_slide1d(feat_out, feat_in, i, mct, mat, mgg, A_SIZE,
                         C_SIZE, FIN_SIZE, FOUT_SIZE);
    }
    right_shift_array(feat_out, QUANT_BITS, FOUT_SIZE*FOUT_SIZE);
    print_array2d(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d(gold_quant, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

