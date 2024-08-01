//
// Created by tarsio on 21/07/2024.
//

#include <stdio.h>
#include "include/util.h"


void print_array1d(const int *array, int size, const char *name) {
    int r;
    printf("%s", name);
    for (r = 0; r < size; r++) {
        printf("%d, ", array[r]);
    };
    printf("\n");
}

void print_array2d(const int *array, int row, int col, const char *name) {
    int r, c;
    printf("%s\n", name);
    for (r = 0; r < row; r++) {
        for (c = 0; c < col; c++) {
            printf("%d, ", array[r * col + c]);
        }
        printf("\n");
    };
    printf("\n");
}


void compare_array1d(const int *array1, const int *array2, int size, const char *name) {
    int r;
    printf("%s\n", name);
    for (r = 0; r < size; r++) {
        if (array1[r] != array2[r]){
            printf("Index=%d m1=%d m2=%d\n", r, array1[r], array2[r]);
        }
    };
    printf("\n");
}


void convert_int_to_float(const int *int_array, float *float_array, int length) {
    int i;
    for (i = 0; i < length; i++) {
        float_array[i] = (float)int_array[i];
    }
}

void init_array(int *array, int size) {
    int i;
    for (i = 0; i < size; i++) {
        array[i] = 0;
    };
}


void right_shift_array(int *array, int shift, int size) {
    int i;
    for (i = 0; i < size; i++) {
        array[i] = array[i] >> shift;
    };
}