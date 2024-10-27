#include "convolution_float.h"
#include "util_float.h"
#include "init.h"
#include "build_float.h"
#include "sim_float.h"

int main() {
    int i;
    const float *mg;
    float mgg[M_SIZE] = {};
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    for (i=0; i < W_SIZE; i++) {
        mg = weight + W_SIZE*i;
        to_bg(mgg, mq, mb, mg, B_SIZE, M_SIZE);
        filter1d_float(feat_out, feat_in, i, mct, mat, mgg, A_SIZE,
                       C_SIZE, M_SIZE, FIN_SIZE, FOUT_SIZE);
    }

    print_array2d_float(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d_float_to_int(gold, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

