#include "lib/include/convolution.h"
#include "lib/include/util.h"

int main() {
    const int m23[2 * 3] = {
        0, 1, 2,
        3, 4, 5
    };
    const int m32[3 * 2] = {
        0, 1,
        2, 3,
        4, 5
    };

    int m22[2 * 2] = {0};
    int m22_gold[2 * 2] = {
        10, 13,
        28, 40
    };
    int m33[3 * 3] = {0};
    int m33_gold[3 * 3] = {
        3, 4, 5,
        9, 14, 19,
        15, 24, 33
    };

    int row1 = 2, col1 = 3, row2 = 3, col2 = 2;

    matrix_mul(m22, m23, m32, row1, col1, col2);
    print_array2d(m22, row1, col2, "M22");
    matrix_mul(m33, m32, m23, row2, col2, col1);
    print_array2d(m33, row2, col1, "M33");

    return 0;
}

