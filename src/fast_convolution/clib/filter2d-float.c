#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test2d/init.h"
#include "test2d/build.h"
#include "test2d/bind_nest.h"
#include "test2d/example.h"


int main() {
    float feat_out[FOUT_SIZE * FOUT_SIZE] = {0};

    float matf[A_SIZE * C_SIZE] = {0};
    float mctf[C_SIZE * C_SIZE] = {0};

    convert_int_to_float(mat, matf, C_SIZE * A_SIZE);
    convert_int_to_float(mct, mctf, C_SIZE * C_SIZE);

    to_bg(mgg, mq, mb, mg, B_SIZE, C_SIZE);

    filter2d_slide2d_float(feat_out, feat_in, mctf, matf, mgg, A_SIZE, C_SIZE, FIN_SIZE, FOUT_SIZE);
    print_array2d_float(feat_out, FOUT_SIZE, FOUT_SIZE, "fout: ");


    return 0;
}

