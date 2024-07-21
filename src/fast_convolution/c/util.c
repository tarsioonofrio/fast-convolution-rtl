//
// Created by tarsio on 21/07/2024.
//

#include <stdio.h>
#include "util.h"


void print_array_float(const float *array, int size, const char *name) {
    int r;
    printf("%s", name);
    for (r=0; r < size; r++) {
        printf("%.3f\t", array[r]);
    };
    printf("\n");
}