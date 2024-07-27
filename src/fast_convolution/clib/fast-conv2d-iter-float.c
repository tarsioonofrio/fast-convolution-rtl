#include <stdio.h>
#include "libs/convolution.h"
#include "libs/util.h"
#include "test2d/init.h"
#include "test2d/build.h"
#include "test2d/example.h"


int main() {
    int i;
    int ms[A1_SIZE * A2_SIZE] = {0};
    float msf[A1_SIZE * A2_SIZE] = {0};
    float mss[C1_SIZE * C2_SIZE] = {0};
    float mss2f[A1_SIZE * A2_SIZE] = {0};
    float mdd[C1_SIZE * C2_SIZE] = {0};

    float ma1tf[A1_SIZE * C1_SIZE] = {0};
    float ma2tf[A2_SIZE * C2_SIZE] = {0};
    float ma2f[A2_SIZE * C2_SIZE] = {0};
    float mc1tf[C1_SIZE * C1_SIZE] = {0};
    float mc2tf[C2_SIZE * C2_SIZE] = {0};
    float mc2f[C2_SIZE * C2_SIZE] = {0};
    float mdf[C1_SIZE * C2_SIZE] = {0};
    float md2f[C1_SIZE * C2_SIZE] = {0};

    convert_int_to_float(ma1t, ma1tf, C1_SIZE * A1_SIZE);
    convert_int_to_float(ma2t, ma2tf, C2_SIZE * A2_SIZE);
    convert_int_to_float(mc1t, mc1tf, C1_SIZE * C1_SIZE);
    convert_int_to_float(mc2t, mc2tf, C2_SIZE * C2_SIZE);
    convert_int_to_float(md, mdf, C1_SIZE * C2_SIZE);
    matrix_transpose_float(mc2f, mc2tf, C1_SIZE, C2_SIZE);
    matrix_transpose_float(ma2f, ma2tf, A2_SIZE, C2_SIZE);

    print_array2d(ma2t, A2_SIZE, C2_SIZE,  "At2: ");
    print_array2d_float(ma2tf, A2_SIZE, C2_SIZE,  "At2: ");
    print_array2d_float(ma2f, C2_SIZE, A2_SIZE,  "A2: ");

//    print_array2d_float(mdf, C1_SIZE, C2_SIZE,  "D: ");
//    print_array2d_float(mc2f, C1_SIZE, C2_SIZE,  "C2: ");
    matrix_mul_float(md2f, mdf, mc2f, C1_SIZE, C2_SIZE, C2_SIZE);
//    print_array2d_float(md2f, C1_SIZE, C2_SIZE,  "d2: ");
//    print_array2d_float(mc1tf, C1_SIZE, C2_SIZE,  "C1: ");
    matrix_mul_float(mdd, mc1tf, md2f, C1_SIZE, C2_SIZE, C2_SIZE);
//    print_array2d_float(mdd, C1_SIZE, C2_SIZE,  "D: ");
//    print_array2d_float(mggf, C1_SIZE, C2_SIZE,  "G: ");

    hadamart_product_float(mss, mdd, mggf, C1_SIZE * C2_SIZE);
//    print_array2d_float(ma2f, C2_SIZE, A2_SIZE,  "A2: ");
//    print_array2d_float(mss, C1_SIZE, C2_SIZE,  "S: ");

    matrix_mul_float(mss2f, mss, ma2f, C1_SIZE, C2_SIZE, C2_SIZE);
    matrix_mul_float(msf, ma1tf, mss2f, C1_SIZE, C2_SIZE, C2_SIZE);

    printf("s=S*a: ");
    for (i = 0; i < A1_SIZE * A2_SIZE; i++) {
        printf("%.3f\t", msf[i]);
    };
    printf("\n");
    convert_float_to_int(msf, ms, A1_SIZE * A2_SIZE);

    compare_array1d(ms_gold, ms, A1_SIZE * A2_SIZE, "Errors in S != gold");



    return 0;
}

