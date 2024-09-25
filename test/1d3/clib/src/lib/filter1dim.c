//
// Created by tarsio on 15/09/2024.
//

#include <stdlib.h>
#include "convolution.h"
#include "fast_conv.h"
#include "filter1dim.h"

#ifdef __riscv
    #include <riscv-csr.h>
#endif

void filter1d(int *feature_out, const int *feature_in, int index, const int *mc, const int *ma,
              const int *mgg, int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, i;
    int *ms = (int *) malloc((a_size) * sizeof(int));
    int *md = (int *) malloc((c_size) * sizeof(int));

//    void (*fast_func)(int *, const int *, const int *, const int *, const int *, int, int) = fast_conv;

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif


    for (r = index; r < fout_size + index; r++) {
        for (c = 0; c <= fout_size; c = c + a_size) {
            for (i = 0; i < c_size; i++) {
                if (c + i < fin_size) {
                    md[i] = feature_in[r * fin_size + c + i];
                } else {
                    md[i] = 0;
                }
            }
            fast_conv(ms, ma, mgg, mc, md, a_size, c_size);
            for (i = 0; i < a_size; i++) {
                if (c + i < fout_size) {
                    feature_out[(r - index) * fout_size + c + i] += ms[i];
                }
            }
        }
    }

    #ifdef __riscv
        csr_write_mcountinhibit(-1);
    #endif

    free(ms);
    free(md);
}