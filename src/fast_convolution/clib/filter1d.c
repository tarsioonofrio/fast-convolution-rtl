#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/build.h"
#include "test1d/sim.h"



int main() {
    int i;
    const int *mg;
    float mgg[C_SIZE] = {};

    float matf[A_SIZE * C_SIZE] = {0};
    float mctf[C_SIZE * C_SIZE] = {0};
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    convert_int_to_float(mat, matf, C_SIZE * A_SIZE);
    convert_int_to_float(mct, mctf, C_SIZE * C_SIZE);

    for (i=0; i < W_SIZE; i++) {
        mg = weight + W_SIZE*i;
        to_bg(mgg, mq, mb, mg, B_SIZE, C_SIZE);
        filter1d_slide1d_float(feat_out, feat_in, i, mctf, matf, mgg,
                               A_SIZE, C_SIZE, FIN_SIZE, FOUT_SIZE);
    }

    print_array1d_float(feat_out, FOUT_SIZE * FOUT_SIZE, "fout: ");


    return 0;
}

