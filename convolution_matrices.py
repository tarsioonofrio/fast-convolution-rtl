import numpy as np


def wrap_tap_filter(a, b, c):
    def tap_filter(g, d):
        return c * b * g * d

def c3x3_5m20a9e():
    '''
    From Blahut page 166
    Linear, 3x3, 5 multiplications, 20 aditions and 9 extra operations
    :return:
    '''
    a = np.array([
        [1, 0, 0],
        [1, 1, 1],
        [1, -1, 1],
        [1, 2, 4],
        [0, 0, 1]
    ])
    b = a
    g = np.array([1/2, -1/2, -1/6, 1/6, 1])
    c = np.array([
        [2, 0, 0, 0, 0],
        [-1, -2, 2, -1, 2],
        [-2, -1, -3, 0, -1],
        [1, 1, 1, 1, -2],
        [0, 0, 0, 0, 1]
    ])
