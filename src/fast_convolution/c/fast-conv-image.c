#include <stdio.h>
#include "convolution.h"
#include "example.h"
#include "util.h"

#define A_SIZE 3
#define B_SIZE 3
#define C_SIZE 5
#define FIN_SIZE 8
#define FOUT_SIZE 6


int main() {
    const float feature_in[FIN_SIZE*FIN_SIZE] = {
             0,  1,  2,  3,  4,  5,  6,  7,
             8,  9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23,
            24, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 34, 35, 36, 37, 38, 39,
            40, 41, 42, 43, 44, 45, 46, 47,
            48, 49, 50, 51, 52, 53, 54, 55,
            56, 57, 58, 59, 60, 61, 62, 63,
    };
    const float feature_out[FOUT_SIZE*FOUT_SIZE] = {0};

    const float feature_gold[FOUT_SIZE*FOUT_SIZE] = {
            5, 8, 11, 14, 17, 20,
            29, 32, 35, 38, 41, 44,
            53, 56, 59, 62, 65, 68,
            77, 80, 83, 86, 89, 92,
            101, 104, 107, 110, 113, 116,
            125, 128, 131, 134, 137, 140,
    };

    const float mb[C_SIZE*A_SIZE] = {
            1, 0, 0,
            1, 1, 1,
            1, -1, 1,
            1, 2, 4,
            0, 0, 1,
    };
    const float mc[C_SIZE*C_SIZE] = {
        2, -1,-2, 1,0,
        0, -2, -1, 1, 0,
        0, 2, -3, 1, 0,
        0, -1, 0, 1, 0,
        0, 2, -1, -2, 1,
    };
    const float ma[A_SIZE*C_SIZE] = {
        1, 1, 1, 1, 0,
        0, 1, -1, 2, 0,
        0, 1, 1, 4, 1,
    };
    const float mg[B_SIZE] = {0, 1, 2};
    const float mq[C_SIZE] = {1.0f/2.0f, -1.0f/2.0f, -1.0f/6.0f, 1.0f/6.0f, 1.0f};

    float md[C_SIZE] = {0};
    float mdd[C_SIZE] = {0};
    float mbg[C_SIZE] = {0};
    float mgg[C_SIZE] = {0};
    float mss[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    int r, c;
    int a_size = A_SIZE;
    int b_size=B_SIZE;
    int c_size=C_SIZE;

    to_bg(mb, mg, mq, mbg, mgg, b_size, c_size);

    for (c=0; c < FIN_SIZE; c=c+A_SIZE) {
        for (r=0; r < c_size; r++) {
            md[r] = feature_in[r];
            printf("%.3f\t", md[r]);
        };
        print_array_float(md, c_size, "md");
//        fast_conv1d_float(ms, ma, mss, mdd, mgg, mc, md, a_size, c_size);
    }

    fast_conv1d_float(ms, ma, mss, mdd, mgg, mc, md, a_size, c_size);


    return 0;
}

