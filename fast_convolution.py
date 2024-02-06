import numpy as np
import sympy as sy


class C3x3_5m20a9e():
    '''
    From Blahut page 166
    Linear, 3x3, 5 multiplications, 20 aditions and 9 extra operations
    :return:
    '''
    _rin = 5
    _rout = 3
    _a = [
        [1, 0, 0],
        [1, 1, 1],
        [1, -1, 1],
        [1, 2, 4],
        [0, 0, 1]
    ]
    _b = _a
    _n = [[1, 2], [-1, 2], [-1, 6], [1, 6], [1, 1]]
    _c = [
        [2, 0, 0, 0, 0],
        [-1, -2, 2, -1, 2],
        [-2, -1, -3, 0, -1],
        [1, 1, 1, 1, -2],
        [0, 0, 0, 0, 1]
    ]

    def __init__(self, gv):
        a = sy.Matrix(self._a)
        b = sy.Matrix(self._b)
        c = sy.Matrix(self._c)
        n = sy.Matrix([sy.Rational(d, q) for d, q in self._n])

        g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(self._rout))))
        f = sy.Matrix(sy.symbols(" ".join(f"f_{i}" for i in range(self._rin))))
        bg = sy.diag(*(b * g).tolist())
        bgn = sy.diag(*bg * n)
        subs = {k: v for k, v in zip(g.values(), gv)}
        gs = bgn.subs(subs)
        self.a = a
        self.c = c
        self.gs = gs
        self.s = sy.MatMul(a.T, gs, c.T, f)

    def __call__(self, fv):
        out = self.a.T * self.gs * self.c.T * sy.Matrix(fv)
        return out

