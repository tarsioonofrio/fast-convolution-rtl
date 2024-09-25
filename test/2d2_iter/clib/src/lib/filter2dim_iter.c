//
// Created by tarsio on 15/09/2024.
//

#include <stdlib.h>
#include "convolution.h"
#include "fast_conv_iter.h"
#include "filter2dim.h"

#ifdef __riscv
    #include <riscv-csr.h>
#endif


void filter2d(int *feature_out, const int *feature_in, int fin_size, int fout_size, int type_conv,
              type_struct_conv *params) {
    int r, c, rd, cd;
    int a1_size = params->a1_size;
    int a2_size = params->a2_size;
    int c1_size = params->c1_size;
    int c2_size = params->c2_size;
    int *ms = (int *) malloc((a1_size * a1_size) * sizeof(int));
    int *md = (int *) malloc((c1_size * c1_size) * sizeof(int));

    #ifdef __riscv
        csr_write_mcountinhibit(0);
    #endif

    for (r = 0; r < fout_size; r = r + a1_size) {
        for (c = 0; c <= fout_size; c = c + a2_size) {
            for (rd = 0; rd < c1_size; rd++) {
                for (cd = 0; cd < c2_size; cd++) {
                    if ((r + rd < fin_size) && (c + cd < fin_size)) {
                        md[rd * c1_size + cd] = feature_in[r * fin_size + rd * fin_size + c + cd];
                    } else {
                        md[rd * c1_size + cd] = 0;
                    }
                }
            }
            fast_conv_iter(ms, params->ma1, params->mc1, params->mgg, params->ma2, params->mc2, md,
                           a1_size, a2_size, c1_size, c2_size);
            for (rd = 0; rd < a1_size; rd++) {
                for (cd = 0; cd < a2_size; cd++) {
                    if (c + rd < fout_size) {
                        feature_out[r * fout_size + rd * fout_size + c + cd] = ms[rd * a1_size + cd];
                    }
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
