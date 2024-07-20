#include <stdio.h>
#include "convolution.h"
#include "example.h"

#define A_SIZE 3
#define B_SIZE 3
#define C_SIZE 5

void to_bg(const float *mb, const float *mg, const float *mq, float *mbg, float *mgg, int b_size, int c_size);

int main() {
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
    const float md[C_SIZE] = {0, 1, 2, 3, 4};
    const float mg[B_SIZE] = {0, 1, 2};
    const float mq[C_SIZE] = {1.0f/2.0f, -1.0f/2.0f, -1.0f/6.0f, 1.0f/6.0f, 1.0f};

    float mdd[C_SIZE] = {0};
    float mbg[C_SIZE] = {0};
    float mgg[C_SIZE] = {0};
    float mss[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    int r;
    int a_size = A_SIZE;
    int b_size=B_SIZE;
    int c_size=C_SIZE;

    to_bg(mb, mg, mq, mbg, mgg, b_size, c_size);
    fast_conv1d_float(ms, ma, mss, mdd, mgg, mc, md, a_size, c_size);

    printf("s=S*a: ");
    for (r=0; r < a_size; r++) {
        printf("%.3f\t", ms[r]);
    };
    printf("\n");

    return 0;
}

void
to_bg(const float *mb, const float *mg, const float *mq, float *mbg, float *mgg, int b_size, int c_size) {
    // G=q.(b*g)
    // bg=b*g
    matrix_mul_float(mbg, mb, mg, c_size, b_size, 1);
//    printf("bg=b*g: ");
//    for (r=0; r < c_size; r++) {
//        printf("%.3f\t", mbg[r]);
//    };
//    printf("\n");

    // G=q.bg
    hadamart_product_float(mgg, mq, mbg, c_size);
//    printf("G=q.bg: ");
//    for (r=0; r < c_size; r++) {
//        printf("%.3f\t", mgg[r]);
//    };
//    printf("\n");

}

