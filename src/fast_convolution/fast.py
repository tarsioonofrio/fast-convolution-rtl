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
        [2, 0, 0, 0, 0],
        [-1, -2, 2, -1, 2],
        [-2, -1, -3, 0, -1],
        [1, 1, 1, 1, -2],
        [0, 0, 0, 0, 1],
    ]
    _n = [1, 1, 1, 1, 1, 1]

    a = sy.Matrix(_a)
    b = sy.Matrix(_b)
    c = sy.Matrix(_c)
    q = sy.Matrix([i for i in _n])
    return a, b, c, q


def wrap_conv_manual_factored(gv):
    a, b, c, q = conv_manual_factored()

    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(a.shape[0]))))
    bg = sy.diag(*(b * g).tolist())
    bgn = sy.diag(*(bg * q))
    subs = {k: v for k, v in zip(g.values(), gv)}
    gs = bgn.subs(subs)
    return wrap_convolution(c, gs, a)


def recursive_log2(n):
    def _recursive_log2(n):
        return [e for e, b in enumerate(bin(n)[2::][::-1]) if b == "1"]

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
        [None for c in range(len(lst_in[0]))] for r in range(len(lst_in))
    ]
    for r, row in enumerate(lst_in):
        for c, col in enumerate(row):
            lst_out[r][c] = recursive_log2(col)
    return lst_out


def log2_matrix(lst):
    def log2_rational(p, q):
        p0 = sy.UnevaluatedExpr(sy.Pow(2, p, evaluate=False))
        q0 = sy.Pow(
            sy.UnevaluatedExpr(sy.Pow(2, q, evaluate=False)), -1, evaluate=False
        )
        return p0 * q0

    mtx = sy.zeros(len(lst), len(lst[0]))
    for er, r in enumerate(lst):
        for ec, c in enumerate(r):
            if "z" in c:
                n = sum(
                    [
                        c["s"]
                        * sy.UnevaluatedExpr(sy.Pow(2, z, evaluate=False))
                        for z in c["z"]
                    ]
                )
            elif "p" in c:
                p = sum(
                    [
                        (
                            c["s"]
                            * sy.UnevaluatedExpr(sy.Pow(2, p, evaluate=False))
                        )
                        for p in c["p"]
                    ]
                )
                # q = sum([
                #     (c["s"] * sy.Pow(sy.UnevaluatedExpr(
                #         sy.Pow(2, q, evaluate=False)), -1, evaluate=False)
                #      )
                #     for q in c["q"]
                # ])
                if len(c["q"]) == 1:
                    _q = sy.UnevaluatedExpr(
                        sy.Pow(2, c["q"][0], evaluate=False)
                    )
                    q = sy.Pow(_q, -1, evaluate=False)
                else:
                    q = c["q"]
                n = p * q
            else:
                n = 0
            mtx[er, ec] = n
    return mtx


def matrix_to_log2(mtx):
    return log2_matrix(log2_lst(mtx))


def count_sums(mtx):
    m_log = matrix_to_log2(mtx)
    m_sum = [
        [1 if -1 in m.args else len(m.args) for m in r] for r in m_log.tolist()
    ]
    return np.sum(m_sum)


def wrap_convolution(c, bg, a):
    def convolution(f):
        tr = c.T * sy.Matrix(f)
        m = sy.HadamardProduct(tr, bg.T, evaluate=True)
        inv = a.T * m
        # out = a.T * bg * c.T * sy.Matrix(f)
        return inv

    return convolution


def to_filter(c, bg, a):
    return a.T * bg * c.T


def wrap_convolution2d(c1, c2, bg, a1, a2):
    def convolution(f):
        tr = c1.T * sy.Matrix(f) * c2
        m = sy.HadamardProduct(tr, bg, evaluate=True)
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


def conv1d(g, c, q, b, a):
    bg = g_to_bg(q, b, g)
    f = wrap_convolution(c, bg, a)
    return f


def toomcook_conv1d(d_size, g_size, points, g):
    c, q, b, a = toom_cook(d_size, g_size, points)
    f = conv1d(g, c, q, b, a)
    return f


def conv2d(g, c1, q1, b1, a1, c2, q2, b2, a2):
    bg = g_to_bg2d(q1, b1, q2, b2, g)
    f = wrap_convolution2d(c1, c2, bg, a1, a2)
    return f


def toomcook_conv2d(d_size, g_size, points, g):
    c1, q1, b1, a1 = toom_cook(d_size, g_size, points)
    c2, q2, b2, a2 = toom_cook(d_size, g_size, points)
    f = conv2d(g, c1, q1, b1, a1, c2, q2, b2, a2)
    return f


def filter1d_slide2d(filt, in_arr, out_shape, index, in_size=5, out_size=3):
    out_arr = np.zeros(out_shape, dtype=int)
    for r in range(index, out_shape[0] + index):
        for c in range(0, out_shape[1], out_size):
            f = in_arr[r, c : c + in_size]
            if len(f) == in_size:
                out = filt(f).flat()
                out_arr[r - index, c : c + out_size] = out
            else:
                tmp_in_size = in_size - len(f)
                zeros = tmp_in_size * [0]
                out = filt(f.tolist() + zeros)
                tmp_out_size = out_shape[0] - c
                out_arr[r - index, c : c + tmp_out_size] = out[:tmp_out_size]
    return out_arr


def filter1d_slide2d_count(out_shape, out_size):
    count = len(list(range(out_shape[0]))) * len(
        range(0, out_shape[1], out_size)
    )
    return count


def filter2d_slide2d(filt, in_arr, out_shape, in_size=(5, 5), out_size=(3, 3)):
    out_arr = np.zeros(out_shape, dtype=int)
    for r in range(0, out_shape[0], out_size[0]):
        for c in range(0, out_shape[1], out_size[1]):
            feat = in_arr[r : r + in_size[0], c : c + in_size[1]]
            if tuple(feat.shape) == tuple(in_size):
                out_tmp = filt(feat)
                out_arr[r : r + out_size[0], c : c + out_size[1]] = out_tmp
            else:
                row_in = feat.shape[0]
                col_in = feat.shape[1]
                new_feat = np.zeros((in_size[0], in_size[1]), dtype=int)
                new_feat[:row_in, :col_in] = feat
                out_tmp = filt(new_feat)
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


def csa_lst(mtx, positive=True):
    lst = log2_lst(mtx)
    signal = 1 if positive else -1
    max_pow = max_power(lst, signal)
    max_lst = [
        [
            [
                1 if len(c) > 0 and p in c["z"] and c["s"] == signal else 0
                for c in r
            ]
            for r in lst
        ]
        for p in range(max_pow + 1)
    ]
    return max_lst


def max_power(lst, positive=True):
    signal = 1 if positive else -1
    max_pow = max(
        [0]
        + [
            max(
                [0]
                + [max(c["z"]) for c in r if len(c) > 0 and c["s"] == signal]
            )
            for r in lst
        ]
    )
    return max_pow


def csa_config(a, c):
    config = {
        (n, s): max_power(log2_lst(lst), positive=typ)
        for lst, n in zip([a.T, c.T], ["a", "c"])
        for typ, s in zip([True, False], ["p", "n"])
    }
    return config


def write_csa_config(config, path):
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "config.txt", "w") as f:
        for (n, s), p in config.items():
            f.write(f"{p} {n} {s}\n")


def csa_parcels(a, c):
    return {
        (n, s): csa_lst(lst, positive=typ)
        for lst, n in zip([a.T, c.T], ["a", "c"])
        for typ, s in zip([True, False], ["p", "n"])
    }


def write_csa_parcels(csa, path):
    path.mkdir(parents=True, exist_ok=True)

    with open(path / "info.txt", "w") as f:
        for (n, s), lst in csa.items():
            f.write(f"{np.sum(lst)} {n} {s}\n")

    for (n, s), lst in csa.items():
        with open(path / f"{n}{s}.txt", "w") as f:
            for power in lst:
                for line in power:
                    f.write(" ".join(map(str, line)) + "\n")
                f.write("\n")
