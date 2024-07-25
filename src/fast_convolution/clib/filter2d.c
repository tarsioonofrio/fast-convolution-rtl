#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test1d/init.h"
#include "test1d/sim.h"


int main() {
    const float feature_in[FIN_SIZE * FIN_SIZE] = {
            0, 1, 2, 3, 4, 5, 6, 7,
            8, 9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23,
            24, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 34, 35, 36, 37, 38, 39,
            40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 53, 54, 55,
            56, 57, 58, 59, 60, 61, 62, 63,
    };
    float feature_out[FOUT_SIZE * FOUT_SIZE] = {0};

    const float feature_gold[FOUT_SIZE * FOUT_SIZE] = {
            5, 8, 11, 14, 17, 20,
            29, 32, 35, 38, 41, 44,
            53, 56, 59, 62, 65, 68,
            77, 80, 83, 86, 89, 92,
            101, 104, 107, 110, 113, 116,
            125, 128, 131, 134, 137, 140,
    };

    const float mb[C_SIZE * A_SIZE] = {
            1, 0, 0,
            1, 1, 1,
            1, -1, 1,
            1, 2, 4,
            0, 0, 1,
    };
    const float mc[C_SIZE * C_SIZE] = {
            2, -1, -2, 1, 0,
            0, -2, -1, 1, 0,
            0, 2, -3, 1, 0,
            0, -1, 0, 1, 0,
            0, 2, -1, -2, 1,
    };
    const float ma[A_SIZE * C_SIZE] = {
            1, 1, 1, 1, 0,
            0, 1, -1, 2, 0,
            0, 1, 1, 4, 1,
    };
    const float mg[B_SIZE] = {0, 1, 2};
    const float mq[C_SIZE] = {1.0f / 2.0f, -1.0f / 2.0f, -1.0f / 6.0f, 1.0f / 6.0f, 1.0f};

    float md[C_SIZE] = {0};
    float mgg[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    to_bg(mgg, mq, mb, mg);

    filter1d_slide2d_float(feature_out, feature_in, mc, ma, md, mgg, ms, A_SIZE, C_SIZE, FIN_SIZE, FOUT_SIZE);
    print_array2d_float(feature_out, FOUT_SIZE, FOUT_SIZE, "fout: ");


    return 0;
}

