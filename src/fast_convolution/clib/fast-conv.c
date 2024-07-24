#include <stdio.h>
#include "libs/convolution.h"
#include "test1d/init.h"
#include "test1d/build.h"
#include "test1d/example.h"

#define A_SIZE 3
#define B_SIZE 3
#define C_SIZE 5

int main() {

    float mgg[C_SIZE] = {0};
    float ms[A_SIZE] = {0};

    int r;
    int a_size = A_SIZE;
    int b_size = B_SIZE;
    int c_size = C_SIZE;

    to_bg(mgg, mq, mb, mg, b_size, c_size);
    fast_conv1d_float(ms, ma, mgg, mc, md, a_size, c_size);

    printf("s=S*a: ");
    for (r = 0; r < a_size; r++) {
        printf("%.3f\t", ms[r]);
    };
    printf("\n");

    return 0;
}

