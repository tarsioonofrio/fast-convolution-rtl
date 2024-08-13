//
// Created by tarsio on 01/08/2024.
//

#ifndef C_UTIL_FLOAT_H
#define C_UTIL_FLOAT_H

void print_array1d_float(const float *array, int size, const char *name);

void print_array2d_float(const float *array, int row, int col, const char *name);

void print_array2d_float_int(const float *array, int row, int col, const char *name);

void compare_array1d_float(const float *array1, const float *array2, int size, const char *name);

void compare_array1d_float_to_int(const float *array1, const float *array2, int size, const char *name);

#endif //C_UTIL_FLOAT_H
