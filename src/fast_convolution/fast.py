import itertools

import numpy as np
import sympy as sy


def conv_manual_factorization():
    """
    From Blahut page 164
    Linear, 3x3, 6 multiplications, 10 aditions and 0 extra operations
    :return:
    """
    _rin = 5
    _rout = 3
    _a = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]]
    _b = _a
    _c = [
        [1, 0, 0, 0, 0, 0],
        [-1, -1, 0, 1, 0, 0],
        [-1, 1, -1, 0, 1, 0],
        [0, -1, -1, 0, 0, 1],
        [0, 0, 1, 0, 0, 0],
    ]
    _n = [1, 1, 1, 1, 1, 1]
    a = sy.Matrix(_a)
    b = sy.Matrix(_b)
    c = sy.Matrix(_c)
    q = sy.Matrix([i for i in _n])
    return c, q, b, a


def wrap_conv_manual_factored(gv):
    a, b, c, q = conv_manual_factorization()
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(a.shape[0]))))
    bg = sy.diag(*(b * g).tolist())
    bgn = sy.diag(*(bg * q))
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bgn.subs(subs)
    return wrap_convolution(c, gs, a)


def wrap_convolution(c, bg, a, quant=0):
    def convolution(f):
        tr = c.T * sy.Matrix(f)
        m_ = sy.HadamardProduct(tr, sy.Matrix(bg), evaluate=True)
        m = (
            m_
            if quant == 0
            else np.right_shift(np.array(m_).astype(int), quant)
        )
        inv = a.T * m
        return inv

    return convolution


def to_filter(c, bg, a):
    return a.T * bg * c.T


def wrap_convolution2d(c1, c2, bg, a1, a2, quant=0):
    def convolution(f):
        tr = c1.T * sy.Matrix(f) * c2
        m_ = sy.HadamardProduct(tr, sy.Matrix(bg), evaluate=True)
        m = (
            m_
            if quant == 0
            else np.right_shift(np.array(m_).astype(int), quant)
        )
        inv = a1.T * m * a2
        return inv

    return convolution


def toom_cook(d_size, g_size, points):
    x = sy.symbols("x")
    di = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(d_size))))
    gi = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(g_size))))
    dx = sum([i * x**e for e, i in enumerate(di)])
    gx = sum([i * x**e for e, i in enumerate(gi)])
    sx = gx * dx
    xi = [x**i for i in range(1, sy.degree(sx.expand(), x) + 1)]
    s_degree = d_size + g_size - 1
    bi = [sy.nsimplify(p) for p in points]
    assert s_degree == len(bi), print(
        f"b_degree: {d_size} != len(bi): {len(bi)}"
    )
    di = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(d_size))))
    gi = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(g_size))))
    _am = [[(b**e) for e, d in enumerate(di)] for b in bi if b != sy.oo]
    _bm = [[(b**e) for e, d in enumerate(gi)] for b in bi if b != sy.oo]
    bi_inf = [x for x in bi if x != sy.oo]
    _q = [
        1 / sy.expand(np.prod([(b0 - b) for b in i]))
        for b0, i in zip(
            bi_inf, itertools.combinations(reversed(bi_inf), len(bi_inf) - 1)
        )
    ]
    if sy.oo in bi:
        _a_inf = [[0] * (len(di) - 1) + [1]]
        am = sy.Matrix(_am + _a_inf)
        _b_inf = [[0] * (len(gi) - 1) + [1]]
        bm = sy.Matrix(_bm + _b_inf)
        q = _q + [1]
    else:
        am = sy.Matrix(_am)
        bm = sy.Matrix(_bm)
        q = _q

    # bg_mtx = sy.diag(*(sy.diag(*cq) * b_mtx * gi).tolist())
    # bg_mtx = g2bg(cq, b_mtx)
    cd = [
        sy.expand(np.prod([(x - b) for b in i if b != sy.oo]))
        for i in itertools.combinations(reversed(bi), len(bi) - 1)
    ]
    c0 = sy.Matrix([s.subs({x: 0}) for s in cd])
    c1 = sy.Matrix([[d.coeff(c, 1) for c in xi] for d in cd])
    cm = sy.Matrix(c0.T.tolist() + c1.T.tolist())
    return cm, sy.Matrix(q), bm, am


def g_to_bg(q, b, g):
    return sy.diag(*(sy.diag(*q) * b * sy.Matrix(g)).tolist()).diagonal()


def g_to_bg2d(q1, b1, q2, b2, g):
    #  Works with 2d output or input of different sizes
    # bg = ((sy.diag(*q2) * b2) * sy.Matrix(g) * (sy.diag(*q1) * b1).T).T
    bg = (sy.diag(*q2) * b2) * sy.Matrix(g) * (sy.diag(*q1) * b1).T
    return bg


def conv1d(g_, c, q, b, a, quant=0):
    g = g_ if quant == 0 else np.left_shift(g_, quant)
    bg_ = g_to_bg(q, b, g)
    bg = (
        bg_ if quant == 0 else np.round(np.array(bg_).astype(float)).astype(int)
    )
    f = wrap_convolution(c, bg, a, quant)
    return f


def toomcook_conv1d(d_size, g_size, points, g, quant=0):
    c, q, b, a = toom_cook(d_size, g_size, points)
    f = conv1d(g, c, q, b, a, quant)
    return f


def conv2d(g_, c, q, b, a, quant=0):
    g = g_ if quant == 0 else np.left_shift(g_, quant)
    bg = g_to_bg2d(q[0], b[0], q[1], b[1], g)
    f = wrap_convolution2d(c[0], c[1], bg, a[0], a[1], quant=quant)
    return f


def toomcook_conv2d(d_size, g_size, points, g, quant=0):
    c1, q1, b1, a1 = toom_cook(d_size, g_size, points)
    c2, q2, b2, a2 = toom_cook(d_size, g_size, points)
    f = conv2d(g, c1, q1, b1, a1, c2, q2, b2, a2, quant=quant)
    return f


def filter1d_slide2d(
    tap_filter, in_arr, out_shape, index, in_size=5, out_size=3
):
    out_arr = np.zeros(out_shape, dtype=int)
    for r in range(index, out_shape[0] + index):
        for c in range(0, out_shape[1], out_size):
            f = in_arr[r, c : c + in_size]
            if len(f) == in_size:
                out = tap_filter(f).flat()
                out_arr[r - index, c : c + out_size] = out
            else:
                tmp_in_size = in_size - len(f)
                zeros = tmp_in_size * [0]
                out = tap_filter(f.tolist() + zeros)
                tmp_out_size = out_shape[0] - c
                out_arr[r - index, c : c + tmp_out_size] = out[:tmp_out_size]
    return out_arr


def sliding1d_window_2d(in_arr, out_arr, out_shape, in_size=5, out_size=3):
    list_in = []
    list_out = []
    for r in range(0, out_shape[0]):
        for c in range(0, out_shape[1], out_size):
            f = in_arr[r, c : c + in_size]
            if len(f) == in_size:
                list_in.append(f.reshape(-1))
                list_out.append(out_arr[r, c : c + out_size].reshape(-1))
            else:
                tmp_in_size = in_size - len(f)
                zeros = tmp_in_size * [0]
                f2 = np.array(f.tolist() + zeros)
                list_in.append(f2.reshape(-1))
                tmp_out_size = out_shape[0] - c
                new_out = np.zeros((out_size), dtype=int)
                new_out[:tmp_out_size] = out_arr[r, c : c + tmp_out_size]
                list_out.append(new_out.reshape(-1))
    return list_in, list_out


def filter1d_slide2d_count(out_shape, out_size):
    count = len(list(range(out_shape[0]))) * len(
        range(0, out_shape[1], out_size)
    )
    return count


def filter2d_slide2d(
    tap_filter, in_arr, out_shape, in_size=(5, 5), out_size=(3, 3)
):
    out_arr = np.zeros(out_shape, dtype=int)
    for r in range(0, out_shape[0], out_size[0]):
        for c in range(0, out_shape[1], out_size[1]):
            feat = in_arr[r : r + in_size[0], c : c + in_size[1]]
            if tuple(feat.shape) == tuple(in_size):
                out_tmp = tap_filter(feat)
                out_arr[r : r + out_size[0], c : c + out_size[1]] = out_tmp
            else:
                row_in = feat.shape[0]
                col_in = feat.shape[1]
                new_feat = np.zeros((in_size[0], in_size[1]), dtype=int)
                new_feat[:row_in, :col_in] = feat
                out_tmp = tap_filter(new_feat)
                row_out, col_out = out_arr[
                    r : r + out_size[0], c : c + out_size[1]
                ].shape
                out_arr[r : r + row_out, c : c + col_out] = out_tmp[
                    :row_out, :col_out
                ]
    return out_arr


def filter2d_slide2d_count(out_shape, out_size):
    count = len(list(range(0, out_shape[0], out_size[0]))) * len(
        range(0, out_shape[1], out_size[1])
    )
    return count


def sliding2d_window2d(
    in_arr, out_arr, out_shape, in_size=(5, 5), out_size=(3, 3)
):
    list_in = []
    list_out = []
    for r in range(0, out_shape[0], out_size[0]):
        for c in range(0, out_shape[1], out_size[1]):
            feat = in_arr[r : r + in_size[0], c : c + in_size[1]]
            if tuple(feat.shape) == tuple(in_size):
                list_in.append(feat.reshape(-1))
                new_out = out_arr[r : r + out_size[0], c : c + out_size[1]]
                list_out.append(new_out.reshape(-1))
            else:
                row_in = feat.shape[0]
                col_in = feat.shape[1]
                new_feat = np.zeros((in_size[0], in_size[1]), dtype=int)
                new_feat[:row_in, :col_in] = feat
                list_in.append(new_feat.reshape(-1))
                new_out = np.zeros((out_size[0], out_size[1]), dtype=int)
                row_out, col_out = out_arr[
                    r : r + out_size[0], c : c + out_size[1]
                ].shape
                new_out[:row_out, :col_out] = out_arr[
                    r : r + row_out, c : c + col_out
                ]
                list_out.append(new_out.reshape(-1))
    return list_in, list_out


def c3x3_5m20a9e(g):
    """
    From Blahut page 166
    Linear, 3x3, 5 multiplications, 20 aditions and 9 extra operations
    :return:
    """
    points = [0, -1, 1, -2, np.inf]
    c, cq, b, a = toom_cook(3, 3, points)
    bg = g_to_bg(cq, b, g)
    f = wrap_convolution(c, bg, a)
    return f
