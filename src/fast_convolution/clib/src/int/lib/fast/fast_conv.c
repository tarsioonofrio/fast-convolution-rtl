//
// Created by tarsio on 13/09/2024.
//

#include <stdlib.h>
#include "convolution.h"
#include "fast_conv.h"


void fast_conv(int *ms, const int *ma, const int *mgg, const int *mc, const int *md, int a_size, int c_size) {
    int *mss = (int *) malloc((c_size) * sizeof(int));
    int *mdd = (int *) malloc((c_size) * sizeof(int));

    init_array(mss, c_size);
    init_array(mdd, c_size);
    init_array(ms, a_size);

    // D=ct*d
    matrix_mul(mdd, mc, md, c_size, c_size, 1);
    // S=D.G
    hadamart_product(mss, mdd, mgg, c_size);
    // s=S*a
    matrix_mul(ms, ma, mss, a_size, c_size, 1);

    free(mss);
    free(mdd);
}


void fast_conv_iter(int *ms, const int *ma1t, const int *mc1t, const int *mgg,
               const int *ma2, const int *mc2, const int *md,
               int a1_size, int a2_size, int c1_size, int c2_size) {

    int *mss = (int *) malloc((c1_size * c2_size) * sizeof(int));
    int *mss2 = (int *) malloc((a1_size * c1_size) * sizeof(int));
    int *mdd = (int *) malloc((c1_size * c2_size) * sizeof(int));
    int *md2 = (int *) malloc((c1_size * c2_size) * sizeof(int));
    // int *ma2 = (int *) malloc((a2_size * c2_size) * sizeof(int));
    // int *mc2 = (int *) malloc((c2_size * c2_size) * sizeof(int));

    init_array(ms, a1_size * a2_size);
    init_array(mss, c1_size * c2_size);
    init_array(mss2, a1_size * c1_size);
    init_array(mdd, c1_size * c2_size);
    init_array(md2, c1_size * c2_size);
    // init_array(ma2, a2_size * c2_size);
    // init_array(mc2, c2_size * c2_size);

#ifdef __riscv
    csr_write_mcountinhibit(0);
#endif

    // matrix_transpose(mc2, mc2t, c1_size, c2_size);
    // matrix_transpose(ma2, ma2t, a2_size, c2_size);
    matrix_mul(md2, md, mc2, c1_size, c2_size, c2_size);
    matrix_mul(mdd, mc1t, md2, c1_size, c2_size, c2_size);
    hadamart_product(mss, mdd, mgg, c1_size * c2_size);
    matrix_mul(mss2, mss, ma2, c1_size, c2_size, a2_size);
    matrix_mul(ms, ma1t, mss2, a1_size, c2_size, a2_size);

#ifdef __riscv
    csr_write_mcountinhibit(-1);
#endif

    free(mss);
    free(mss2);
    free(mdd);
    free(md2);
    // free(ma2);
    // free(mc2);
}