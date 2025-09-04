#include "convolution.h"
#include "util.h"
#include "init.h"
#include "build.h"
#include "sim.h"

#ifdef __riscv
    #include <riscv-csr.h>
#endif


int main() {
    inhibit_all();

    int i;
    const int *mgg;
    int feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    for (i=0; i < W_SIZE; i++) {
        mgg = weight_gg_quant + M_SIZE*i;
        // print_array1d(mgg, C_SIZE, "G: ");
        filter1d(feat_out, feat_in, i, mct, mat, mgg, A_SIZE,
                 C_SIZE, M_SIZE, FIN_SIZE, FOUT_SIZE);
    }
    right_shift_array(feat_out, QUANT_BITS, FOUT_SIZE*FOUT_SIZE);
    print_array2d(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d(gold_quant, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}
