//
// Created by tarsio on 21/07/2024.
//

#ifndef C_UTIL_H
#define C_UTIL_H

void print_array1d(const int *array, int size, const char *name);
void print_array2d(const int *array, int row, int col, const char *name);

void compare_array1d(const int *array1, const int *array2, int size, const char *name);

void convert_int_to_float(const int *int_array, float *float_array, int length);

void init_array(int *array, int size);

void right_shift_array(int *array, int shift, int size);

#endif //C_UTIL_H
