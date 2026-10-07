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


def conv_tolimlin_4x3():
    """
    Tolimieri linear convolution (4x3) exported from maple-pkg-convolution.

    Construction:
      factors = [x, x**2 - 1, x**2 + 1]
      algorithm = conv.TolimLin(4, factors, x, rhs_length=3)

    The matrix Q holds one denominator per column of C (factored out) so that
    the Hadamard stage uses Q * diag(Bg).
    """
    _c = [
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, -1, 1, -1, -1, 1, -1, -1],
        [0, 1, 0, 1, -1, 0, 1, 0],
        [0, -1, 1, -1, 1, -1, 1, 0],
        [-1, 1, 0, 1, 1, 0, -1, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
    ]
    _q = [
        1,
        sy.Rational(1, 2),
        sy.Rational(1, 2),
        sy.Rational(1, 2),
        sy.Rational(1, 2),
        sy.Rational(1, 2),
        sy.Rational(1, 2),
        1,
    ]
    _b = [
        [1, 0, 0],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 0],
        [1, 0, -1],
        [1, 1, -1],
        [0, 1, 0],
        [0, 0, 1],
    ]
    _a = [
        [1, 0, 0, 0],
        [1, 0, 1, 0],
        [1, 1, 1, 1],
        [0, 1, 0, 1],
        [1, 0, -1, 0],
        [1, 1, -1, -1],
        [0, 1, 0, -1],
        [0, 0, 0, 1],
    ]
    c = sy.Matrix(_c)
    q = sy.Matrix(_q)
    b = sy.Matrix(_b)
    a = sy.Matrix(_a)
    return c, q, b, a


def wrap_conv_manual_factored(gv):
    a, b, c, q = conv_manual_factorization()
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(a.shape[0]))))
    bg = sy.diag(*(b * g).tolist())
    bgn = sy.diag(*(bg * q))
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bgn.subs(subs)
    return wrap_convolution(c, gs, a)


def _wrap_signed_matrix(values, nbits):
    if nbits is None:
        return values
    values = sy.Matrix(values)
    modulus = 1 << nbits
    sign_bit = 1 << (nbits - 1)
    return sy.Matrix(
        values.rows,
        values.cols,
        lambda row, col: (
            (int(values[row, col]) % modulus) - modulus
            if int(values[row, col]) % modulus >= sign_bit
            else int(values[row, col]) % modulus
        ),
    )


def _arithmetic_shift_matrix(values, shift):
    values = sy.Matrix(values)
    if shift == 0:
        return values
    return sy.Matrix(
        values.rows,
        values.cols,
        lambda row, col: int(values[row, col]) >> shift,
    )


def wrap_convolution(c, bg, a, quant=0, nbits=None):
    def convolution(f):
        tr = _wrap_signed_matrix(c.T * sy.Matrix(f), nbits)
        m_ = sy.HadamardProduct(tr, sy.Matrix(bg), evaluate=True)
        m = _arithmetic_shift_matrix(m_, quant)
        m = _wrap_signed_matrix(m, nbits)
        inv = _wrap_signed_matrix(a.T * m, nbits)
        return inv

    return convolution


def to_filter(c, bg, a):
    return a.T * bg * c.T


def wrap_convolution2d(
    c1, c2, bg, a1, a2, quant=0, nbits=None, product_nbits=None
):
    def convolution(f):
        # Transform modules expose NBITS-wide outputs between matrix stages.
        tr_partial = _wrap_signed_matrix(c1.T * sy.Matrix(f), nbits)
        tr = _wrap_signed_matrix(tr_partial * c2, nbits)
        m_ = sy.HadamardProduct(tr, sy.Matrix(bg), evaluate=True)
        m = _arithmetic_shift_matrix(m_, quant)
        arithmetic_bits = product_nbits if product_nbits is not None else nbits
        m = _wrap_signed_matrix(m, arithmetic_bits)
        inv_partial = _wrap_signed_matrix(a1.T * m, arithmetic_bits)
        inv = _wrap_signed_matrix(inv_partial * a2, arithmetic_bits)
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


def sliding1d_window2d(
    in_arr, out_arr, out_shape, in_size=5, out_size=3, return_output=False
):
    list_data = []
    for r in range(0, out_shape[0]):
        for c in range(0, out_shape[1], out_size):
            f = np.array(in_arr[r, c : c + in_size])
            if len(f) == in_size:
                if return_output:
                    list_data.append(
                        np.array(out_arr[r, c : c + out_size]).reshape(-1)
                    )
                else:
                    list_data.append(f.reshape(-1))
            else:
                tmp_in_size = in_size - len(f)
                zeros = tmp_in_size * [0]
                f2 = np.array(f.tolist() + zeros)
                tmp_out_size = out_shape[0] - c
                new_out = np.zeros((out_size), dtype=int)
                new_out[:tmp_out_size] = out_arr[r, c : c + tmp_out_size]
                if return_output:
                    list_data.append(np.array(new_out).reshape(-1))
                else:
                    list_data.append(f2.reshape(-1))
    return list_data


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
    in_arr,
    out_arr,
    out_shape,
    in_size=(5, 5),
    out_size=(3, 3),
    return_output=True,
):
    list_data = []
    for r in range(0, out_shape[0], out_size[0]):
        for c in range(0, out_shape[1], out_size[1]):
            feat = in_arr[r : r + in_size[0], c : c + in_size[1]]
            if tuple(feat.shape) == tuple(in_size):
                new_out = out_arr[r : r + out_size[0], c : c + out_size[1]]
                if return_output:
                    list_data.append(new_out.reshape(-1))
                else:
                    list_data.append(feat.reshape(-1))
            else:
                row_in = feat.shape[0]
                col_in = feat.shape[1]
                new_feat = np.zeros((in_size[0], in_size[1]), dtype=int)
                new_feat[:row_in, :col_in] = feat
                new_out = np.zeros((out_size[0], out_size[1]), dtype=int)
                row_out, col_out = out_arr[
                    r : r + out_size[0], c : c + out_size[1]
                ].shape
                new_out[:row_out, :col_out] = out_arr[
                    r : r + row_out, c : c + col_out
                ]
                if return_output:
                    list_data.append(new_out.reshape(-1))
                else:
                    list_data.append(new_feat.reshape(-1))
    return list_data


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
