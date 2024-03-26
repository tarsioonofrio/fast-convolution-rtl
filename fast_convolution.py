import math
import itertools

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


def recursive_log2(n):
    def _recursive_log2(n):
        return [e for e, b in enumerate(bin(n)[2::][::-1]) if b == '1']

    if n == 0:
        return {}

    sign = -1 if n < 0 else 1

    if isinstance(n, sy.Integer):
        exp_z = _recursive_log2(n)
        out = {
            "s": sign,
            "z": exp_z,
        }
    else:
        exp_p = _recursive_log2(n.p)
        exp_q = _recursive_log2(n.q)
        out = {
            "s": sign,
            "p": exp_p,
            "q": exp_q,
        }
    return out


def log2_lst(mtx):
    lst_in = mtx.tolist()
    lst_out = [
        [None for c in range(len(lst_in[0]))]
        for r in range(len(lst_in))
    ]
    for r, row in enumerate(lst_in):
        for c, col in enumerate(row):
            lst_out[r][c] = recursive_log2(col)
    return lst_out


def log2_matrix(lst):
    def log2_rational(p, q):
        p0 = sy.UnevaluatedExpr(sy.Pow(2, p, evaluate=False))
        q0 = sy.Pow(sy.UnevaluatedExpr(
            sy.Pow(2, q, evaluate=False)), -1, evaluate=False
        )
        return p0 * q0

    mtx = sy.zeros(len(lst), len(lst[0]))
    for er, r in enumerate(lst):
        for ec, c in enumerate(r):
            if 'z' in c:
                n = sum([
                    c["s"] * sy.UnevaluatedExpr(sy.Pow(2, z, evaluate=False))
                    for z in c["z"]
                ])
            elif 'p' in c:
                p = sum([
                    (c["s"] * sy.UnevaluatedExpr(
                        sy.Pow(2, p, evaluate=False))
                     )
                    for p in c["p"]
                ])
                q = sum([
                    (c["s"] * sy.Pow(sy.UnevaluatedExpr(
                        sy.Pow(2, q, evaluate=False)), -1, evaluate=False)
                     )
                    for q in c["q"]
                ])
                n = p * q
            else:
                n = 0
            mtx[er, ec] = n
    return mtx


def wrap_convolution(a, bg, c):
    def convolution(fv):
        out = wrap_filter(a, bg, c) * sy.Matrix(fv)
        return out
    return convolution


def wrap_filter(a, bg, c):
    return a.T * bg * c.T


def c3x3_5m20a9e(gv):
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

    a = sy.Matrix(_a)
    b = sy.Matrix(_b)
    c = sy.Matrix(_c)
    n = sy.Matrix([sy.Rational(d, q) for d, q in _n])

    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(_rout))))
    # f = sy.Matrix(sy.symbols(" ".join(f"f_{i}" for i in range(_rin))))
    bg = sy.diag(*(b * g).tolist())
    bgn = sy.diag(*(bg * n))
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bgn.subs(subs)
    # s = sy.MatMul(a.T, gs, c.T, f)
    return wrap_convolution(a, gs, c)


def c3x3_6m10a0e(gv):
    '''
    From Blahut page 164
    Linear, 3x3, 6 multiplications, 10 aditions and 0 extra operations
    :return:
    '''
    _rin = 5
    _rout = 3
    _a = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 0],
        [1, 0, 1],
        [0, 1, 1]
    ]
    _b = _a
    _c = [
        [2, 0, 0, 0, 0],
        [-1, -2, 2, -1, 2],
        [-2, -1, -3, 0, -1],
        [1, 1, 1, 1, -2],
        [0, 0, 0, 0, 1]
    ]
    _n = [1, 1, 1, 1, 1, 1]

    a = sy.Matrix(_a)
    b = sy.Matrix(_b)
    c = sy.Matrix(_c)
    n = sy.Matrix([i for i in _n])

    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(_rout))))
    bg = sy.diag(*(b * g).tolist())
    bgn = sy.diag(*(bg * n))
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bgn.subs(subs)
    return wrap_convolution(a, gs, c)


def toom_cook(d_size, g_size, points):
    x = sy.symbols("x")
    di = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(d_size))))
    gi = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(g_size))))
    dx = sum([i*x**e for e, i in enumerate(di)])
    gx = sum([i*x**e for e, i in enumerate(gi)])
    sx = gx*dx
    xi = [x**i for i in range(1, sy.degree(sx.expand(), x) + 1)]
    s_degree = d_size + g_size - 1
    bi = [sy.nsimplify(p) for p in points]
    assert s_degree == len(bi), print(
        f"b_degree: {d_size} != len(bi): {len(bi)}"
    )
    di = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(d_size))))
    gi = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(g_size))))
    _a_mtx = [[(b**e) for e, d in enumerate(di)] for b in bi if b != sy.oo]
    _b_mtx = [[(b**e) for e, d in enumerate(gi)] for b in bi if b != sy.oo]
    bi_inf = [x for x in bi if x != sy.oo]
    _cq = [
        1/sy.expand(np.prod([(b0 - b) for b in i]))
        for b0, i in
        zip(bi_inf, itertools.combinations(reversed(bi_inf), len(bi_inf)-1))
    ]
    if sy.oo in bi:
        _a_inf = [[0] * (len(di) - 1) + [1]]
        a_mtx = sy.Matrix(_a_mtx + _a_inf)
        _b_inf = [[0] * (len(gi) - 1) + [1]]
        b_mtx = sy.Matrix(_b_mtx + _b_inf)
        cq = _cq + [1]
    else:
        a_mtx = sy.Matrix(_a_mtx)
        b_mtx = sy.Matrix(_b_mtx)
        cq = _cq

    # bg_mtx = sy.diag(*(sy.diag(*cq) * b_mtx * gi).tolist())
    # bg_mtx = g2bg(cq, b_mtx)
    cd = [
        sy.expand(np.prod([(x - b) for b in i if b != sy.oo]))
        for i in itertools.combinations(reversed(bi), len(bi)-1)
    ]
    c0 = sy.Matrix([s.subs({x: 0}) for s in cd])
    c1 = sy.Matrix([[d.coeff(c, 1) for c in xi] for d in cd])
    c_mtx = sy.Matrix(c0.T.tolist() + c1.T.tolist())
    return c_mtx, cq, b_mtx, a_mtx


def g2bg(cq, b, g):
    return sy.diag(*(sy.diag(*cq) * b * sy.Matrix(g)).tolist())
