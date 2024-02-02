# from Blahut Appendix A A collection of cyclic convolution algorithms, page 427
# cyclic, 3x3, 4 multiplications, 11 aditions and 2 extra operations
c3x3m4a11e2 = {
    'a': [
        [1, 1, 1],
        [1, 0, -1],
        [1, 1, -2]
    ],
    'c': [
        [1, 1, 0, -1],
        [1, -1, -1, 2],
        [1, 0, 1, -1]
    ],
    'g': 1 / 3,
    'b': [
        [1, 1, 1],
        [3, 0, -3],
        [0, 3, -3],
        [1, 1, -2]
    ],
},
