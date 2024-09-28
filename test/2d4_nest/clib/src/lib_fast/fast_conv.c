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
