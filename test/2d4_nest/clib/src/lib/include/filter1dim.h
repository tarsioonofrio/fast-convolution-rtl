//
// Created by tarsio on 15/09/2024.
//

#ifndef FAST_CONV_FILTER1DIM_H
#define FAST_CONV_FILTER1DIM_H

void filter1d(int *feature_out, const int *feature_in, int index, const int *mc, const int *ma,
              const int *mgg, int a_size, int c_size, int fin_size, int fout_size);


#endif //FAST_CONV_FILTER1DIM_H
