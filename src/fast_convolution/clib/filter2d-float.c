#include "libs/convolution.h"
#include "libs/util.h"
#include "test2d/init.h"
#include "test2d/bind_nest_float.h"
#include "test2d/sim_float.h"

int main() {
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    filter2d_slide2d_float(feat_out, feat_in, mc_nest, ma_nest, weight_gg,
                           A1_SIZE, C1_SIZE, FIN_SIZE, FOUT_SIZE);

    print_array2d_float(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");
    compare_array1d_float_to_int(gold, feat_out, FOUT_SIZE * FOUT_SIZE, "Errors in S != gold");

    return 0;
}

