//
// Created by tarsio on 21/07/2024.
//

#include <stdio.h>
#include "util.h"


void print_array1d_float(const float *array, int size, const char *name) {
    int r;
    printf("%s", name);
    for (r = 0; r < size; r++) {
        printf("%.3f\t", array[r]);
    };
    printf("\n");
}


void print_array2d_float(const float *array, int row, int col, const char *name) {
    int r, c;
    printf("%s\n", name);
    for (r = 0; r < row; r++) {
        for (c = 0; c < col; c++) {
            printf("%.3f\t", array[r * row + c]);
        }
        printf("\n");

    };
    printf("\n");
}