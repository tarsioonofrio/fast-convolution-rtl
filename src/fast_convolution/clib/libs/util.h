//
// Created by tarsio on 21/07/2024.
//

#ifndef C_UTIL_H
#define C_UTIL_H

void print_array1d_float(const float *array, int size, const char *name);

void print_array2d_float(const float *array, int row, int col, const char *name);

void convert_float_to_int(const float *float_array, int *int_array, int length);
void convert_int_to_float(const int *int_array, float *float_array, int length);
#endif //C_UTIL_H
