#include <stdio.h>
#include "convolution.h"
#include "example.h"

#define A_SIZE 3
#define B_SIZE 3
#define C_SIZE 5

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
    float md[C_SIZE] = {0, 1, 2, 3, 4};
    float mg[B_SIZE] = {0, 1, 2};
    float mq[C_SIZE] = {1/2, -1/2, -1/6, 1/6, 1};
    float mdd[C_SIZE] = {0};
    float mbg[C_SIZE] = {0};
    float mgg[C_SIZE] = {0};
    float mss[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    int r;

    // G=q.(b*g)
    // bg=b*g
    matrix_mul_float(mb, mg, mbg, C_SIZE, B_SIZE, 1);
    printf("bg=b*g: ");
    for (r=0; r < C_SIZE; r++) {
        printf("%f\t", mbg[r]);
    };
    printf("\n");

    // G=q.bg
    hadamart_product_float(mbg, mq, mgg, C_SIZE);
    printf("G=q.bg: ");
    for (r=0; r < C_SIZE; r++) {
        printf("%f\t", mgg[r]);
    };
    printf("\n");

    // D=ct*d
    matrix_mul_float(mc, md, mdd, C_SIZE, C_SIZE, 1);
    printf("D=ct*d: ");
    for (r=0; r < C_SIZE; r++) {
        printf("%f\t", mdd[r]);
    };
    printf("\n");

    // S=D.G
    hadamart_product_float((float *)mdd, mgg, mss, C_SIZE);
    printf("S=D.G: ");
    for (r=0; r < C_SIZE; r++) {
        printf("%f\t", mss[r]);
    };
    printf("\n");

    // s=S*a
    matrix_mul_float(mss, ma, ms, A_SIZE, C_SIZE, 1);
    printf("s=S*a: ");
    for (r=0; r < B_SIZE; r++) {
        printf("%f\t", ms[r]);
    };
    printf("\n");

    return 0;
}

