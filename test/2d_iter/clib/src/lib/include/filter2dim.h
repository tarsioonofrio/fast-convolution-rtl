//
// Created by tarsio on 15/09/2024.
//

#ifndef FAST_CONV_FILTER2DIM_H
#define FAST_CONV_FILTER2DIM_H

#include "convolution.h"

void filter2d(int *feature_out, const int *feature_in, int fin_size, int fout_size, int type_conv,
              type_struct_conv *params);

#endif //FAST_CONV_FILTER2DIM_H