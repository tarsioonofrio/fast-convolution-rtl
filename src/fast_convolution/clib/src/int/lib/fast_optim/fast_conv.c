//
// Created by tarsio on 13/09/2024.
//

#include "convolution.h"
#include <stdlib.h>
#include "fast_conv.h"
#include "optim.h"


void fast_conv(int *ms, const int *ma, const int *mgg, const int *mc, const int *md, int a_size, int c_size) {
    int *mss = (int *) malloc((c_size) * sizeof(int));
    int *mdd = (int *) malloc((c_size) * sizeof(int));

    init_array(mss, c_size);
    init_array(mdd, c_size);
    init_array(ms, a_size);

    matrix_mul_shift_noloop_c(mdd, md);
    hadamart_product_noloop(mss, mdd, mgg);
    matrix_mul_shift_noloop_a(ms, mss);

    free(mss);
    free(mdd);
}
