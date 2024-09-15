//
// Created by tarsio on 13/09/2024.
//

#ifndef FAST_CONV_FAST_CONV_H
#define FAST_CONV_FAST_CONV_H

void fast_conv(int *ms, const int *ma, const int *mgg, const int *mc, const int *md, int a_size, int c_size);

void fast_conv_iter(int *ms, const int *ma1t, const int *mc1t, const int *mgg,
               const int *ma2, const int *mc2, const int *md,
               int a1_size, int a2_size, int c1_size, int c2_size);

#endif //FAST_CONV_FAST_CONV_H
