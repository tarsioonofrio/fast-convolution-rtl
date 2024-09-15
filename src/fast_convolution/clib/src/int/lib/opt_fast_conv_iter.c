//
// Created by tarsio on 13/09/2024.
//

#include <stdlib.h>
#include "convolution.h"
#include "fast_conv.h"
#include "optim.h"


void fast_conv(int *ms, const int *ma1t, const int *mc1t, const int *mgg,
                    const int *ma2, const int *mc2, const int *md,
                    int a1_size, int a2_size, int c1_size, int c2_size) {

    int *mss = (int *) malloc((c1_size * c2_size) * sizeof(int));
    int *mss2 = (int *) malloc((a1_size * c1_size) * sizeof(int));
    int *mdd = (int *) malloc((c1_size * c2_size) * sizeof(int));
    int *md2 = (int *) malloc((c1_size * c2_size) * sizeof(int));

    init_array(ms, a1_size * a2_size);
    init_array(mss, c1_size * c2_size);
    init_array(mss2, a1_size * c1_size);
    init_array(mdd, c1_size * c2_size);
    init_array(md2, c1_size * c2_size);

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif

    matrix_mul_shift_noloop_c2(md2, md);
    matrix_mul_shift_noloop_c1t(mdd, md2);
    hadamart_product_noloop_iter(mss, mdd, mgg);
    matrix_mul_shift_noloop_a2(mss2, mss);
    matrix_mul_shift_noloop_a1t(ms, mss2);

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