//
// Created by tarsio on 01/08/2024.
//

#include <stdlib.h>
#include "include/convolution_float.h"
#include "include/util_float.h"

void matrix_mul_float(float *out, const float *in1, const float *in2, int row1, int col2_row1, int col2) {
    int r, c, k;
    for (r = 0; r < row1; r++) {
        for (c = 0; c < col2; c++) {
            for (k = 0; k < col2_row1; k++) {
                out[r * col2 + c] += in1[r * col2_row1 + k] * in2[k * col2 + c];
            }
        }
    }
}

void matrix_transpose_float(float *out, const float *in, int row, int col) {
    int r, c;
    for (r = 0; r < row; r++) {
        for (c = 0; c < col; c++) {
            out[c * row + r] = in[r * col + c];
        }
    }
}

void hadamart_product_float(float *out, const float *in1, const float *in2, int row) {
    int r;
    for (r = 0; r < row; r++) {
        out[r] = in1[r] * in2[r];
    }
}

void fast_conv_float(float *ms, const float *ma, const float *mgg, const float *mc, const float *md, int a_size,
                     int c_size) {
    float *mss = (float *) malloc((c_size) * sizeof(float));
    float *mdd = (float *) malloc((c_size) * sizeof(float));

    init_array_float(mss, c_size);
    init_array_float(mdd, c_size);
    init_array_float(ms, a_size);

    // D=ct*d
    matrix_mul_float(mdd, mc, md, c_size, c_size, 1);
    // S=D.G
    hadamart_product_float(mss, mdd, mgg, c_size);
    // s=S*a
    matrix_mul_float(ms, ma, mss, a_size, c_size, 1);
    free(mss);
    free(mdd);
}

void fast_conv_nest_float(float *ms, const float *ma1t, const float *mc1t, const float *mgg,
                          const float *ma2t, const float *mc2t, const float *md,
                          int a1_size, int a2_size, int c1_size, int c2_size) {

    float *mss = (float *) malloc((c1_size * c2_size) * sizeof(float));
    float *mss2 = (float *) malloc((a1_size * c1_size) * sizeof(float));
    float *mdd = (float *) malloc((c1_size * c2_size) * sizeof(float));
    float *ma2 = (float *) malloc((a2_size * c2_size) * sizeof(float));
    float *mc2 = (float *) malloc((c2_size * c2_size) * sizeof(float));
    float *md2 = (float *) malloc((c1_size * c2_size) * sizeof(float));

    init_array_float(ms, a1_size * a2_size);
    init_array_float(mss, c1_size * c2_size);
    init_array_float(mss2, a1_size * c1_size);
    init_array_float(mdd, c1_size * c2_size);
    init_array_float(ma2, a2_size * c2_size);
    init_array_float(mc2, c2_size * c2_size);
    init_array_float(md2, c1_size * c2_size);


    matrix_transpose_float(mc2, mc2t, c1_size, c2_size);
    matrix_transpose_float(ma2, ma2t, a2_size, c2_size);
    matrix_mul_float(md2, md, mc2, c1_size, c2_size, c2_size);
    matrix_mul_float(mdd, mc1t, md2, c1_size, c2_size, c2_size);
    hadamart_product_float(mss, mdd, mgg, c1_size * c2_size);
    matrix_mul_float(mss2, mss, ma2, c1_size, c2_size, a2_size);
    matrix_mul_float(ms, ma1t, mss2, a1_size, c2_size, a2_size);

    free(mss);
    free(mss2);
    free(mdd);
    free(ma2);
    free(mc2);
    free(md2);
}


void to_bg(float *mgg, const float *mq, const float *mb, const float *mg, int b_size, int c_size) {
    int i;
    float *mbg = (float *) malloc((c_size) * sizeof(float));
    float *mqf = (float *) malloc((c_size) * sizeof(float));
    init_array_float(mbg, c_size);
    init_array_float(mqf, c_size);

    for (i = 0; i < c_size; i++) {
        mqf[i] = mq[i * 2] / mq[i * 2 + 1];
    }
    // G=q.(b*g)
    // bg=b*g
    matrix_mul_float(mbg, mb, mg, c_size, b_size, 1);
    //print_array1d_float(mbg, c_size, "bg=b*g: ");
    // G=q.bg
    hadamart_product_float(mgg, mqf, mbg, c_size);
    //print_array1d_float(mgg, c_size, "G=q.bg: ");

    free(mbg);
    free(mqf);
}

void filter1d_float(float *feature_out, const float *feature_in, int index, const float *mc, const float *ma,
                    const float *mgg, int a_size, int c_size, int fin_size, int fout_size) {
    int r, c, i;
    float *ms = (float *) malloc((a_size) * sizeof(float));
    float *md = (float *) malloc((c_size) * sizeof(float));

    for (r = index; r < fout_size + index; r++) {
        for (c = 0; c <= fout_size; c = c + a_size) {
            for (i = 0; i < c_size; i++) {
                if (c + i < fin_size) {
                    md[i] = feature_in[r * fin_size + c + i];
                } else {
                    md[i] = 0;
                }
            }
            fast_conv_float(ms, ma, mgg, mc, md, a_size, c_size);
            for (i = 0; i < a_size; i++) {
                if (c + i < fout_size) {
                    feature_out[(r - index) * fout_size + c + i] += ms[i];
                }
            }
        }
    }
    free(ms);
    free(md);
}

void filter2d(float *feature_out, const float *feature_in, int fin_size, int fout_size, int type_conv, type_struct_conv *params) {
    int r, c, rd, cd;
    int a1_size = params->a1_size;
    int a2_size = params->a2_size;
    int c1_size = params->c1_size;
    int c2_size = params->c2_size;
    float *ms = (float *) malloc((a1_size * a2_size) * sizeof(float));
    float *md = (float *) malloc((c1_size * c2_size) * sizeof(float));

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
//            print_array2d_float_int(md, c1_size, c2_size, "D: ");
            if (type_conv == KRON) {
                fast_conv_float(ms, params->ma, params->mgg, params->mc, md,
                                a1_size * a2_size, c1_size * c2_size);
            } else if (type_conv == NEST){
                fast_conv_nest_float(ms, params->ma1, params->mc1, params->mgg, params->ma2, params->mc2,
                                     md, a1_size, a2_size, c1_size, c2_size);
            }
            for (rd = 0; rd < a1_size; rd++) {
                for (cd = 0; cd < a2_size; cd++) {
                    if (c + rd < fout_size) {
                        feature_out[r * fout_size + rd * fout_size + c + cd] = ms[rd * a1_size + cd];
                    }
                }
            }
        }
    }
    free(ms);
    free(md);
}

void convert_float_to_int(const float *float_array, int *int_array, int length) {
    int i;
    for (i = 0; i < length; i++) {
        int_array[i] = (int)float_array[i];  // Converte o float para int
    }
}

void init_array_float(float *array, int size) {
    int i;
    for (i = 0; i < size; i++) {
        array[i] = 0;
    };
}

