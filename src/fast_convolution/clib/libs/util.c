//
// Created by tarsio on 21/07/2024.
//

#include <stdlib.h>
#include <stdio.h>
#include "util.h"


void print_array1d(const int *array, int size, const char *name) {
    int r;
    printf("%s", name);
    for (r = 0; r < size; r++) {
//        printf("%.3f\t", array[r]);
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



void print_array1d_float(const float *array, int size, const char *name) {
    int r;
    printf("%s", name);
    for (r = 0; r < size; r++) {
//        printf("%.3f\t", array[r]);
        printf("%.2f, ", array[r]);
    };
    printf("\n");
}

void print_array2d_float(const float *array, int row, int col, const char *name) {
    int r, c;
    printf("%s\n", name);
    for (r = 0; r < row; r++) {
        for (c = 0; c < col; c++) {
//            printf("%.3f\t", array[r * row + c]);
            printf("%.2f, ", array[r * col + c]);
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
            printf("Err i: %d 1: %d 2: %d\n", r, array1[r], array2[r]);
        }
    };
    printf("\n");
}


void convert_float_to_int(const float *float_array, int *int_array, int length) {
    int i;
    for (i = 0; i < length; i++) {
        int_array[i] = (int)float_array[i];  // Converte o float para int
    }
}

void convert_int_to_float(const int *int_array, float *float_array, int length) {
    int i;
    for (i = 0; i < length; i++) {
        float_array[i] = (float)int_array[i];
    }
}

void init_array(float *array, int size) {
    int i;
    for (i = 0; i < size; i++) {
        array[i] = 0;
    };
}