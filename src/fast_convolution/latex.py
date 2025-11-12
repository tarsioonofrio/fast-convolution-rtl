import click
import numpy as np
import pylatex as tex
import sympy as sy
from scipy import signal
from sympy.physics.quantum import TensorProduct

from fast_convolution.utils import default_convolve

from . import fast, utils


def _to_tex(expr):
    if isinstance(expr, tex.NoEscape):
        return expr
    if isinstance(expr, sy.MatrixBase) or isinstance(expr, sy.Basic):
        return tex.NoEscape(sy.latex(expr))
    if isinstance(expr, np.ndarray):
        return tex.NoEscape(sy.latex(sy.Matrix(expr)))
    return expr


def _flatten(items):
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from _flatten(item)
        else:
            yield item


def append_math(doc, *items, escape=False):
    data = [_to_tex(item) for item in _flatten(items)]
    doc.append(tex.Math(data=data, escape=escape))


def create_document(title, geometry=None):
    doc = tex.Document()
    if geometry:
        doc.preamble.append(tex.Package("geometry", geometry))
    doc.preamble.append(tex.Command("title", title))
    doc.preamble.append(tex.Command("author", "Fast-Convolution Python Library"))
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))
    return doc


def latex_1d(c, b, a, q, path, d_user, g_user_, symbolic=True, quant=0):
    name = (
        "Symbolic"
        if symbolic
        else "Numeric"
        if quant == 0
        else "Numeric Quantized"
    )
    g_user = g_user_ if quant == 0 else sy.Matrix(np.left_shift(g_user_, quant))
    gg_sym = sy.Matrix(
        sy.symbols(" ".join(f"G_{i}" for i in range(q.shape[0])))
    )
    dd_sym = sy.Matrix(
        sy.symbols(" ".join(f"D_{i}" for i in range(q.shape[0])))
    )
    ss_sym = sy.Matrix(
        sy.symbols(" ".join(f"S_{i}" for i in range(a.shape[0])))
    )
    s_sym = sy.Matrix(sy.symbols(" ".join(f"s_{i}" for i in range(a.shape[1]))))

    doc = create_document(f"{name} 1D Convolution", geometry="landscape")

    def math(*items, **kwargs):
        append_math(doc, *items, **kwargs)

    math(r"s = a^t \{[q \odot (bg)] \odot (c^t d)\}", escape=False)
    math("d =", d_user, escape=False)
    math("g =", g_user, escape=False)
    math(
        s_sym,
        "=",
        a.T,
        r"\left\{ \left[",
        q,
        r"\odot \left(",
        b,
        g_user,
        r"\right) \right]",
        r"\odot \left(",
        c.T,
        d_user,
        r"\right) \right\}",
        escape=False,
    )
    gg_num_ = sy.hadamard_product(q, b * g_user)
    gg_num = (
        gg_num_
        if quant == 0
        else sy.Matrix(np.round(np.array(gg_num_).astype(float)).astype(int))
    )

    math(
        gg_sym,
        "=",
        gg_num,
        "=",
        q,
        r"\odot",
        b * g_user,
        "=",
        q,
        r"\odot \left(",
        b,
        g_user,
        r"\right)",
        escape=False,
    )
    dd_num = c.T * d_user
    math(dd_sym, "=", dd_num, "=", c.T, d_user, escape=False)
    math(r"S = G \odot D", escape=False)
    ss_num_ = sy.hadamard_product(gg_num, dd_num)
    ss_num = (
        ss_num_
        if quant == 0
        else sy.Matrix(np.right_shift(np.array(ss_num_).astype(int), quant))
    )

    ss_user = ss_sym if symbolic else ss_num
    gg_user = gg_sym if symbolic else gg_num
    dd_user = dd_sym if symbolic else dd_num
    math(ss_user, "=", gg_user, r"\odot", dd_user, escape=False)
    s_num = a.T * ss_num
    s_user = s_sym if symbolic else s_num
    math(s_user, "=", a.T * ss_user, "=", a.T, ss_user, escape=False)

    math(r"a^{t} =", utils.matrix_to_log2(a.T), escape=False)
    math(r"b =", utils.matrix_to_log2(b), escape=False)
    math(r"c^{t} =", utils.matrix_to_log2(c.T), escape=False)
    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)

    if symbolic is False:
        output_default = signal.convolve(
            d_user, g_user[::-1, ::-1], mode="valid"
        )
        compare_naive = np.all(
            output_default.reshape(-1) == np.array(s_num).reshape(-1)
        )
        print("Result:", compare_naive)


def latex_2d_bind_nest(
    build_data, d1_user, g1_user_, path, symbolic=True, quant=0
):
    name = (
        "Symbolic"
        if symbolic
        else "Numeric"
        if quant == 0
        else "Numeric Quantized"
    )
    g1_user = (
        g1_user_ if quant == 0 else sy.Matrix(np.left_shift(g1_user_, quant))
    )

    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    d2_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[1],
        sy.symbols(
            " ".join(
                f"\\delta_{{{i}}}" for i in range(c1.shape[0] * c2.shape[1])
            )
        ),
    )
    dd_sym = sy.Matrix(
        q1.shape[0],
        q2.shape[0],
        sy.symbols(
            " ".join(f"D_{{{i}}}" for i in range(q1.shape[0] * q2.shape[0]))
        ),
    )
    g2_sym = sy.Matrix(
        b1.shape[1],
        b2.shape[0],
        sy.symbols(
            " ".join(
                f"\\gamma_{{{i}}}" for i in range(b1.shape[1] * b2.shape[0])
            )
        ),
    )
    gg_sym = sy.Matrix(
        q1.shape[0],
        q2.shape[0],
        sy.symbols(
            " ".join(f"G_{{{i}}}" for i in range(q1.shape[0] * q2.shape[0]))
        ),
    )
    ss2_sym = sy.Matrix(
        c1.shape[1],
        c2.shape[1],
        sy.symbols(
            " ".join(f"S_{{{i}}}" for i in range(c1.shape[1] * c2.shape[1]))
        ),
    )

    ss1_sym = sy.Matrix(
        c1.shape[1],
        a1.T.shape[0],
        sy.symbols(
            " ".join(
                f"\\sigma_{{{i}}}" for i in range(c1.shape[1] * a1.T.shape[0])
            )
        ),
    )
    s_sym = sy.Matrix(
        a1.T.shape[0],
        a2.T.shape[0],
        sy.symbols(
            " ".join(f"s_{{{i}}}" for i in range(a1.T.shape[0] * a2.T.shape[0]))
        ),
    )

    doc = create_document(
        f"{name} Nested 2D Convolution", geometry=["a3paper", "landscape"]
    )

    def math(*items, **kwargs):
        append_math(doc, *items, **kwargs)

    math(
        r"s=a_1^t \{[(q_1 \odot b_1) g (q_2 \odot b_2)^t] \odot (c_1^t d c_2)\}a_2",
        escape=False,
    )
    math("d =", d1_user, escape=False)
    math("g =", g1_user, escape=False)
    math(r"G = (q_1 \odot b_1) g (q_2 \odot b_2)^t", escape=False)
    g2_num_ = sy.Matrix(g1_user) * (sy.diag(*q1) * b1).T
    g2_num = (
        g2_num_
        if quant == 0
        else sy.Matrix(np.round(np.array(g2_num_).astype(float)).astype(int))
    )
    math(
        g2_sym,
        "=",
        g2_num,
        "=",
        g1_user,
        r"\odot",
        (sy.diag(*q1) * b1).T,
        "=",
        g1_user,
        r"\left(",
        q1,
        r"\odot",
        b1,
        r"\right)^t",
        escape=False,
    )
    gg_user_ = sy.diag(*q2) * b2 * sy.Matrix(g2_sym if symbolic else g2_num)
    gg_user = (
        gg_user_
        if quant == 0
        else sy.Matrix(np.round(np.array(gg_user_).astype(float)).astype(int))
    )
    g2_user = g2_sym if symbolic else g2_num
    math(
        gg_sym,
        "=",
        gg_user,
        "=",
        sy.diag(*q2) * b2,
        r"\odot",
        g2_user,
        r"= \left(",
        q2,
        r"\odot",
        b2,
        r"\right)",
        g2_sym,
        escape=False,
    )

    math(r"D = c_1^t d c_2", escape=False)
    d2_num = d1_user * c2
    math(d2_sym, "=", d2_num, "=", d1_user, c2, escape=False)
    d2_user = d2_sym if symbolic else d2_num
    dd_num = c1.T * d2_user
    math(dd_sym, "=", dd_num, "=", c1.T, d2_user, escape=False)
    math(r"S = G \odot D", escape=False)
    ss2_num_ = sy.hadamard_product(gg_user, dd_num)
    ss2_num = (
        ss2_num_
        if quant == 0
        else sy.Matrix(np.right_shift(np.array(ss2_num_).astype(int), quant))
    )
    ss_user = ss2_sym if symbolic else ss2_num
    gg_user = gg_sym if symbolic else gg_user
    dd_user = dd_sym if symbolic else dd_num

    math(ss_user, "=", gg_user, r"\odot", dd_user, escape=False)

    math(r"s = a_1^t S a_2", escape=False)
    ss1_num = ss2_num * a2
    ss1_user = ss2_sym * a2 if symbolic else ss1_num
    math(ss1_sym, "=", ss1_user, "=", ss_user, a2, escape=False)
    s_user = a1.T * ss1_sym if symbolic else a1.T * ss1_num
    ss1_user = ss1_sym if symbolic else ss1_num
    math(s_sym, "=", s_user, "=", a1.T, ss1_user, escape=False)
    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)
    # TODO add operations count like in bind_kron function
    if symbolic is False:
        output_default = default_convolve(d1_user, g1_user)
        compare_naive = np.all(
            output_default.reshape(-1) == np.array(s_user).reshape(-1)
        )
        print("Result:", compare_naive)


def latex_2d_bind_kron(build_data, d1_user, g1_user_, path, symbolic, quant=0):
    name = (
        "Symbolic"
        if symbolic
        else "Numeric"
        if quant == 0
        else "Numeric Quantized"
    )
    g1_user = (
        g1_user_ if quant == 0 else sy.Matrix(np.left_shift(g1_user_, quant))
    )
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    aa_shape = (
        a1.shape[0] * a2.shape[0],
        a1.shape[1] * a2.shape[1],
    )
    aa_sym = sy.Matrix(
        aa_shape[0],
        aa_shape[1],
        sy.symbols(
            " ".join(f"A_{i}" for i in range(aa_shape[0] * aa_shape[1]))
        ),
    )
    cc_shape = c1.shape[0] * c2.shape[0], c1.shape[1] * c2.shape[1]
    cc_sym = sy.Matrix(
        cc_shape[0],
        cc_shape[1],
        sy.symbols(
            " ".join(f"C_{i}" for i in range(cc_shape[0] * cc_shape[1]))
        ),
    )
    g1_sym = sy.Matrix(
        b1.shape[1],
        b2.shape[1],
        sy.symbols(
            " ".join(f"g_{{{i}}}" for i in range(b1.shape[1] * b2.shape[1]))
        ),
    )
    g2_sym = sy.Matrix(
        b1.shape[1],
        b1.shape[0],
        sy.symbols(
            " ".join(
                f"\\gamma_{{{i}}}" for i in range(b1.shape[1] * b1.shape[0])
            )
        ),
    )
    gg_sym = sy.Matrix(
        q1.shape[0],
        q2.shape[0],
        sy.symbols(
            " ".join(f"G_{{{i}}}" for i in range(q1.shape[0] * q2.shape[0]))
        ),
    )
    d_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"d_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
        ),
    )
    dd_sym = sy.Matrix(
        q1.shape[0],
        q2.shape[0],
        sy.symbols(
            " ".join(f"D_{{{i}}}" for i in range(q1.shape[0] * q2.shape[0]))
        ),
    )
    ss_sym = sy.Matrix(
        c1.shape[1],
        c2.shape[1],
        sy.symbols(
            " ".join(f"S_{{{i}}}" for i in range(c1.shape[1] * c2.shape[1]))
        ),
    )
    s_sym = sy.Matrix(
        a1.T.shape[0],
        a2.T.shape[0],
        sy.symbols(
            " ".join(f"s_{{{i}}}" for i in range(a1.T.shape[0] * a2.T.shape[0]))
        ),
    )

    doc = create_document(
        f"{name} 2D Kronecker Convolution", geometry=["a3paper", "landscape"]
    )

    def math(*items, **kwargs):
        append_math(doc, *items, **kwargs)

    math(
        r"s=(a_1^t \otimes a_2^t) \{[(q_1 \odot b_1) g (q_2 \odot b_2)^t] \odot (c_1^t \otimes c_2^t)\} d",
        escape=False,
    )
    math("d =", d_sym, "=", d1_user, escape=False)
    math("g =", g1_sym, "=", g1_user, escape=False)
    math(r"G = (q_1 \odot b_1) g (q_2 \odot b_2)^t", escape=False)
    g2_num = sy.Matrix(g1_user) * (sy.diag(*q1) * b1).T
    # g2_num = (
    #     g2_num_
    #     if quant == 0
    #     else sy.Matrix(np.round(np.array(g2_num_).astype(float)).astype(int))
    # )
    math(
        g2_sym,
        "=",
        g2_num,
        "=",
        g1_user,
        r"\odot",
        (sy.diag(*q1) * b1).T,
        "=",
        g1_sym,
        r"\left(",
        q1,
        r"\odot",
        b1,
        r"\right)^t",
        escape=False,
    )
    # breakpoint()
    gg_user_ = sy.diag(*q2) * b2 * sy.Matrix(g2_sym if symbolic else g2_num)
    gg_user = (
        gg_user_
        if quant == 0
        else sy.Matrix(np.round(np.array(gg_user_).astype(float)).astype(int))
    )
    g2_user = g2_sym if symbolic else g2_num
    math(
        gg_sym,
        "=",
        gg_user,
        "=",
        sy.diag(*q2) * b2,
        r"\odot",
        g2_user,
        r"= \left(",
        q2,
        r"\odot",
        b2,
        r"\right)",
        g2_sym,
        escape=False,
    )
    math(r"C = c_1^t \otimes c_2^t", escape=False)
    cc_num = TensorProduct(c1.T, c2.T)
    math("C =", cc_num, "=", c1.T, r"\otimes", c2.T, escape=False)
    math(r"A = a_1^t \otimes a_2^t", escape=False)
    aa_num = TensorProduct(a1.T, a2.T)
    math("A =", aa_num, "=", a1.T, r"\otimes", a2.T, escape=False)
    math(r"D = Cd", escape=False)
    dd_num = cc_num * d1_user.reshape(cc_num.shape[1], 1)
    math(
        dd_sym.reshape(dd_num.shape[0] * dd_num.shape[1], 1),
        "=",
        dd_num,
        "=",
        cc_num,
        d1_user.reshape(cc_num.shape[1], 1),
        escape=False,
    )
    math(r"S = G \odot D", escape=False)
    ss_num_ = sy.hadamard_product(
        gg_user, dd_num.reshape(gg_user.shape[0], gg_user.shape[1])
    )
    ss_num = (
        ss_num_
        if quant == 0
        else sy.Matrix(np.right_shift(np.array(ss_num_).astype(int), quant))
    )
    ss_user = ss_sym if symbolic else ss_num
    gg_user = gg_sym if symbolic else gg_user
    dd_user = (
        dd_sym
        if symbolic
        else dd_num.reshape(gg_user.shape[0], gg_user.shape[1])
    )
    math(ss_user, "=", gg_user, r"\odot", dd_user, escape=False)
    math(r"s = AS", escape=False)
    s_num = aa_num * ss_user.reshape(ss_user.shape[0] * ss_user.shape[1], 1)
    math(
        s_sym.reshape(s_sym.shape[0] * s_sym.shape[1], 1),
        "=",
        s_num,
        "=",
        aa_num,
        ss_user.reshape(ss_user.shape[0] * ss_user.shape[1], 1),
        escape=False,
    )

    math(r"A =", utils.matrix_to_log2(aa_num), escape=False)
    math(r"C =", utils.matrix_to_log2(cc_num), escape=False)
    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)

    if symbolic:
        a_sum = fast.count_sums(aa_num)
        c_sum = fast.count_sums(cc_num)
        text = (
            f"Total multiplications: {len(gg_user)}\n"
            f"Sums:\n"
            f"A: {a_sum}\n"
            f"C: {c_sum}\n"
            f"Total: {a_sum + c_sum}\n"
        )
        with open(path.parent / "info.txt", "w") as f:
            f.write(text)
    else:
        output_default = signal.convolve(
            d1_user, g1_user[::-1, ::-1], mode="valid"
        )
        compare_naive = np.all(
            output_default.reshape(-1) == np.array(s_num).reshape(-1)
        )
        print("Result:", compare_naive)
