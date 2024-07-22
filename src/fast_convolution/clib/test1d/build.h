//
// Created by tarsio on 21/07/2024.
//

#ifndef C_BUILD_H
#define C_BUILD_H

const float mb[C_SIZE * A_SIZE] = {
        1, 0, 0,
        1, 1, 1,
        1, -1, 1,
        1, 2, 4,
        0, 0, 1,
};
const float mc[C_SIZE * C_SIZE] = {
        2, -1, -2, 1, 0,
        0, -2, -1, 1, 0,
        0, 2, -3, 1, 0,
        0, -1, 0, 1, 0,
        0, 2, -1, -2, 1,
};
const float ma[A_SIZE * C_SIZE] = {
        1, 1, 1, 1, 0,
        0, 1, -1, 2, 0,
        0, 1, 1, 4, 1,
};
const float md[C_SIZE] = {0, 1, 2, 3, 4};
const float mg[B_SIZE] = {0, 1, 2};
const float mq[C_SIZE] = {1.0f / 2.0f, -1.0f / 2.0f, -1.0f / 6.0f, 1.0f / 6.0f, 1.0f};


#endif //C_BUILD_H
