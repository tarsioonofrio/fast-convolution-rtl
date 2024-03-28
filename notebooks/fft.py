import numpy as np
import sympy as sy

from sympy import I, pi, sin, cos

# Blahut page 435 Appendix B: A collection of Winograd small FFT algorithms




def wfta2_0m2a0e(gv):
    '''
    From Blahut page 436
    Linear, 3x3, 5 multiplications, 20 aditions and 9 extra operations
    :return:
    '''
    _size = 2
    _a = [
        [1, 1],
        [1, -1],
    ]
    _b = [1, 1]

    _c = [
        [1, 1],
        [1, -1],
    ]

    a = sy.Matrix(_a)
    b = sy.Matrix(_b)
    c = sy.Matrix(_c)

    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(_size))))
    bg = sy.diag(*(b * g).tolist())
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bg.subs(subs)
    s = sy.MatMul(a.T, gs, c.T, f)
    return wrapper_convolution(a, gs, c)


def wfta4_0m8a0e(gv):
    '''
    From Blahut page 436
    Linear, 3x3, 5 multiplications, 20 aditions and 9 extra operations
    :return:
    '''
    _size = 4
    _a = [
        [1, 1, 1, 1],
        [1, -1, 1, -1],
        [1, 0, -1, 0],
        [0, 1, 0, -1]
    ]
    _b = [1, 1, 1, 1]

    _c = [
        [1, 0, 0, 0],
        [0, 0, 1, -I],
        [0, 1, 0, 0],
        [0, 0, 1, I],
    ]

    a = sy.Matrix(_a)
    b = sy.Matrix(_b)
    c = sy.Matrix(_c)

    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(_size))))
    bg = sy.diag(*(b * g).tolist())
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bg.subs(subs)
    s = sy.MatMul(a.T, gs, c.T, f)
    return wrapper_convolution(a, gs, c)
