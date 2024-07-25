#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/build.h"
#include "test1d/sim.h"



int main() {
    const float feature_in[8 * 8] = {
            0, 1, 2, 3, 4, 5, 6, 7,
            8, 9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23,
            24, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 34, 35, 36, 37, 38, 39,
            40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 53, 54, 55,
            56, 57, 58, 59, 60, 61, 62, 63,
    };
    float feature_out[8 * 8] = {0};

    const float feature_gold[6 * 6] = {
            5, 8, 11, 14, 17, 20,
            29, 32, 35, 38, 41, 44,
            53, 56, 59, 62, 65, 68,
            77, 80, 83, 86, 89, 92,
            101, 104, 107, 110, 113, 116,
            125, 128, 131, 134, 137, 140,
    };

    const int mg[B_SIZE] = {0, 1, 2};

    float mgg[C_SIZE] = {0};

    float matf[A_SIZE * C_SIZE] = {0};
    float mctf[C_SIZE * C_SIZE] = {0};

    convert_int_to_float(mat, matf, C_SIZE * A_SIZE);
    convert_int_to_float(mct, mctf, C_SIZE * C_SIZE);

    to_bg(mgg, mq, mb, mg, B_SIZE, C_SIZE);

    filter1d_slide1d_float(feature_out, feature_in, mctf, matf, mgg, A_SIZE, C_SIZE, 8, 6);
    print_array2d_float(feature_out, 6, 6, "fout: ");


    return 0;
}

