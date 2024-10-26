import click
import numpy as np
import pylatex as tex
import sympy as sy
from scipy import signal
from sympy.physics.quantum import TensorProduct

from fast_convolution.utils import default_convolve

from . import fast


def syt(expr):
    return tex.NoEscape(sy.latex(expr))


def doc_append(doc, lst):
    data = [syt(d) if isinstance(d, sy.Matrix) else d for d in lst]
    doc.append(tex.Math(data=data, escape=False))


def build_1d(b, c, a, g_sym, d_sym, q, path):
    gg_sym = sy.Matrix(
        sy.symbols(" ".join(f"G_{i}" for i in range(b.shape[0])))
    )
    dd_sym = sy.Matrix(
        sy.symbols(" ".join(f"D_{i}" for i in range(c.T.shape[1])))
    )
    ss_sym = sy.Matrix(
        sy.symbols(" ".join(f"S_{i}" for i in range(a.T.shape[1])))
    )
    s_sym = sy.Matrix(
        sy.symbols(" ".join(f"s_{i}" for i in range(a.T.shape[0])))
    )

    doc = tex.Document()
    doc.preamble.append(tex.Package("geometry", "a3paper"))
    doc.preamble.append(tex.Command("title", "Symbolic 1D Convolution"))
    doc.preamble.append(
        tex.Command("author", "Fast-Convolution Python Library")
    )
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))

    doc.append(
        tex.Math(
            escape=False, data=[r"s = a^t \{[q \odot (bg)] \odot (c^t d)\}"]
        )
    )
    doc.append(tex.Math(data=["d =", syt(d_sym)], escape=False))
    doc.append(tex.Math(data=["g =", syt(g_sym)], escape=False))
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(s_sym),
                "=",
                syt(a.T),
                r"\left\{ \left[",
                syt(q),
                r"\odot \left(",
                syt(b),
                syt(g_sym),
                r"\right) \right]",
                r"\odot \left(",
                syt(c.T),
                syt(d_sym),
                r"\right) \right\}",
            ],
        )
    )
    gg_num = sy.hadamard_product(q, b * g_sym)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(gg_sym),
                "=",
                syt(gg_num),
                "=",
                syt(q),
                r"\odot",
                syt(b * g_sym),
                "=",
                syt(q),
                r"\odot \left(",
                syt(b),
                syt(g_sym),
                r"\right)",
            ],
        )
    )
    dd_num = c.T * d_sym
    doc.append(
        tex.Math(
            data=[syt(dd_sym), "=", syt(dd_num), "=", syt(c.T), syt(d_sym)]
        )
    )
    doc.append(tex.Math(data=[r"S = G \odot D"], escape=False))
    doc.append(
        tex.Math(
            data=[
                syt(s_sym),
                "=",
                syt(a.T * ss_sym),
                "=",
                syt(a.T),
                syt(ss_sym),
            ]
        )
    )

    doc.append(
        tex.Math(data=[r"a^{t} =", syt(fast.matrix_to_log2(a.T))], escape=False)
    )
    doc.append(
        tex.Math(data=[r"b =", syt(fast.matrix_to_log2(b))], escape=False)
    )
    doc.append(
        tex.Math(data=[r"c^{t} =", syt(fast.matrix_to_log2(c.T))], escape=False)
    )
    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)


def build_2d_bind_nest(init_data, build_data, path):
    # dim, c_len, b_len, a_len = init_data
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    d1_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"d_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
        ),
    )

    d2_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(
                f"\\delta_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0])
            )
        ),
    )
    dd_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"D_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
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
        b2.shape[1],
        sy.symbols(
            " ".join(
                f"\\gamma_{{{i}}}" for i in range(b1.shape[1] * b2.shape[1])
            )
        ),
    )
    gg_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"G_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
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

    doc = tex.Document()
    doc.preamble.append(tex.Package("geometry", "a1paper"))
    doc.preamble.append(tex.Command("title", "Symbolic Nested 2D Convolution"))
    doc.preamble.append(
        tex.Command("author", "Fast-Convolution Python Library")
    )
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))
    doc.append(
        tex.Math(
            escape=False,
            data=[
                r"s=a_1^t \{[(q_1 \odot b_1) g (q_2 \odot b_2)^t] \odot (c_1^t d c_2)\}a_2"
            ],
        )
    )
    doc.append(
        tex.Math(
            data=[r"G = (q_1 \odot b_1) g (q_2 \odot b_2)^t"], escape=False
        )
    )
    g_num2 = sy.Matrix(g1_sym) * (sy.diag(*q1) * b1).T
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(g2_sym),
                "=",
                syt(g_num2),
                "=",
                syt(g1_sym),
                r"\odot",
                syt((sy.diag(*q1) * b1).T),
                "=",
                syt(g1_sym),
                r"\left(",
                syt(q1),
                r"\odot",
                syt(b1),
                r"\right)^t",
            ],
        )
    )

    gg_num = sy.diag(*q2) * b2 * sy.Matrix(g2_sym)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(gg_sym),
                "=",
                syt(gg_num),
                "=",
                syt(sy.diag(*q2) * b2),
                r"\odot",
                syt(g2_sym),
                r"= \left(",
                syt(q2),
                r"\odot",
                syt(b2),
                r"\right)",
                syt(g2_sym),
            ],
        )
    )

    doc.append(tex.Math(data=[r"D = c_1^t d c_2"], escape=False))
    d_num2 = d1_sym * c2
    doc.append(
        tex.Math(
            data=[syt(d2_sym), "=", syt(d_num2), "=", syt(d1_sym), syt(c2)],
            escape=False,
        )
    )
    dd_num = c1.T * d2_sym
    doc.append(
        tex.Math(
            data=[syt(dd_sym), "=", syt(dd_num), "=", syt(c1.T), syt(d2_sym)],
            escape=False,
        )
    )

    doc.append(tex.Math(data=[r"S = G \odot D"], escape=False))
    doc.append(tex.Math(data=[r"s = a_1^t S a_2"], escape=False))
    doc.append(
        tex.Math(
            data=[
                syt(ss1_sym),
                "=",
                syt(ss2_sym * a2),
                "=",
                syt(ss2_sym),
                syt(a2),
            ],
            escape=False,
        )
    )
    doc.append(
        tex.Math(
            data=[
                syt(s_sym),
                "=",
                syt(a1.T * ss1_sym),
                "=",
                syt(a1.T),
                syt(ss1_sym),
            ],
            escape=False,
        )
    )
    try:
        doc.generate_pdf(path / "bind-nest", clean_tex=False)
    except Exception as e:
        click.echo(e)

    # TODO add operations count like in bind_kron function


def build_2d_bind_kron(init_data, build_data, path):
    # dim, c_len, b_len, a_len = init_data
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    d1_user = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"d_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
        ),
    )
    g1_user = sy.Matrix(
        b1.shape[1],
        b2.shape[1],
        sy.symbols(
            " ".join(f"g_{{{i}}}" for i in range(b1.shape[1] * b2.shape[1]))
        ),
    )

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
        c1.T.shape[0],
        c2.T.shape[0],
        sy.symbols(
            " ".join(f"G_{{{i}}}" for i in range(c1.T.shape[0] * c2.T.shape[0]))
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
        c1.T.shape[0],
        c2.T.shape[0],
        sy.symbols(
            " ".join(f"D_{{{i}}}" for i in range(c1.T.shape[0] * c2.T.shape[0]))
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

    doc = tex.Document()
    doc.preamble.append(tex.Package("geometry", "a0paper"))
    doc.preamble.append(
        tex.Command("title", "Symbolic 2D Kronecker Convolution")
    )
    doc.preamble.append(
        tex.Command("author", "Fast-Convolution Python Library")
    )
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))

    doc.append(
        tex.Math(
            escape=False,
            data=[
                r"s=(a_1^t \otimes a_2^t) \{[(q_1 \odot b_1) g (q_2 \odot b_2)^t] \odot (c_1^t \otimes c_2^t)\} d"
            ],
        )
    )
    doc.append(
        tex.Math(
            data=[r"G = (q_1 \odot b_1) g (q_2 \odot b_2)^t"], escape=False
        )
    )
    g2_num = sy.Matrix(g1_user) * (sy.diag(*q1) * b1).T
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(g2_sym),
                "=",
                syt(g2_num),
                "=",
                syt(g1_user),
                r"\odot",
                syt((sy.diag(*q1) * b1).T),
                "=",
                syt(g1_sym),
                r"\left(",
                syt(q1),
                r"\odot",
                syt(b1),
                r"\right)^t",
            ],
        )
    )

    gg_num = sy.diag(*q2) * b2 * sy.Matrix(g2_sym)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(gg_sym),
                "=",
                syt(gg_num),
                "=",
                syt(sy.diag(*q2) * b2),
                r"\odot",
                syt(g2_sym),
                r"= \left(",
                syt(q2),
                r"\odot",
                syt(b2),
                r"\right)",
                syt(g2_sym),
            ],
        )
    )
    doc.append(tex.Math(data=[r"C = c_1^t \otimes c_2^t"], escape=False))
    cc_num = TensorProduct(c1.T, c2.T)
    doc.append(
        tex.Math(
            data=["C =", syt(cc_num), "=", syt(c1.T), r"\otimes", syt(c2.T)],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"A = a_1^t \otimes a_2^t"], escape=False))
    aa_num = TensorProduct(a1.T, a2.T)
    doc.append(
        tex.Math(
            data=["A =", syt(aa_num), "=", syt(a1.T), r"\otimes", syt(a2.T)],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"D = Cd"], escape=False))
    dd_num = cc_num * d1_user.reshape(cc_num.shape[1], 1)
    doc.append(
        tex.Math(
            data=[
                syt(dd_sym.reshape(dd_sym.shape[0] * dd_sym.shape[1], 1)),
                "=",
                syt(dd_num),
                "=",
                syt(cc_num),
                syt(d1_user.reshape(cc_num.shape[1], 1)),
            ]
        )
    )
    doc.append(tex.Math(data=[r"S = G \odot D"], escape=False))
    ss_num = sy.hadamard_product(
        gg_sym, dd_sym.reshape(gg_num.shape[0], gg_num.shape[1])
    )
    doc.append(
        tex.Math(
            data=[
                syt(ss_sym),
                "=",
                syt(ss_num),
                "=",
                syt(gg_sym),
                r"\odot",
                syt(dd_sym),
            ],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"s = AS"], escape=False))
    s_num = aa_num * ss_sym.reshape(ss_sym.shape[0] * ss_sym.shape[1], 1)
    doc.append(
        tex.Math(
            data=[
                syt(s_sym.reshape(s_sym.shape[0] * s_sym.shape[1], 1)),
                "=",
                syt(s_num),
                "=",
                syt(aa_num),
                syt(ss_sym.reshape(ss_sym.shape[0] * ss_sym.shape[1], 1)),
            ]
        )
    )

    doc.append(
        tex.Math(data=[r"A =", syt(fast.matrix_to_log2(aa_num))], escape=False)
    )
    doc.append(
        tex.Math(data=[r"C =", syt(fast.matrix_to_log2(cc_num))], escape=False)
    )
    try:
        doc.generate_pdf(path / "bind-kron", clean_tex=False)
    except Exception as e:
        click.echo(e)

    a_sum = fast.count_sums(aa_num)
    c_sum = fast.count_sums(cc_num)
    text = (
        f"Total multiplications: {len(gg_num)}\n"
        f"Sums:\n"
        f"A: {a_sum}\n"
        f"C: {c_sum}\n"
        f"Total: {a_sum + c_sum}\n"
    )
    with open(path / "info.txt", "w") as f:
        f.write(text)


def example_1d(b, c, a, g_num, d_num, q, path):
    g_sym = sy.Matrix(
        sy.symbols(" ".join(f"g_{i}" for i in range(g_num.shape[0])))
    )
    d_sym = sy.Matrix(
        sy.symbols(" ".join(f"d_{i}" for i in range(c.T.shape[0])))
    )
    gg_sym = sy.Matrix(
        sy.symbols(" ".join(f"G_{i}" for i in range(b.shape[0])))
    )
    dd_sym = sy.Matrix(
        sy.symbols(" ".join(f"D_{i}" for i in range(d_num.shape[0])))
    )
    ss_sym = sy.Matrix(
        sy.symbols(" ".join(f"S_{i}" for i in range(a.T.shape[1])))
    )
    s_sym = sy.Matrix(
        sy.symbols(" ".join(f"s_{i}" for i in range(a.T.shape[0])))
    )

    doc = tex.Document()
    doc.preamble.append(tex.Package("geometry", "a3paper"))
    doc.preamble.append(tex.Command("title", "Numeric 1D Convolution"))
    doc.preamble.append(
        tex.Command("author", "Fast-Convolution Python Library")
    )
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))

    doc.append(
        tex.Math(
            escape=False, data=[r"s = a^t \{[q \odot (bg)] \odot (c^t d)\}"]
        )
    )
    doc.append(
        tex.Math(data=["d =", syt(d_sym), "=", syt(d_num)], escape=False)
    )
    doc.append(
        tex.Math(data=["g =", syt(g_sym), "=", syt(g_num)], escape=False)
    )
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(s_sym),
                "=",
                syt(a.T),
                r"\left\{ \left[",
                syt(q),
                r"\odot \left(",
                syt(b),
                syt(g_num),
                r"\right) \right]",
                r"\odot \left(",
                syt(c.T),
                syt(d_num),
                r"\right) \right\}",
            ],
        )
    )
    gg_num = sy.hadamard_product(q, b * g_num)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(gg_sym),
                "=",
                syt(gg_num),
                "=",
                syt(q),
                r"\odot",
                syt(b * g_num),
                "=",
                syt(q),
                r"\odot \left(",
                syt(b),
                syt(g_num),
                r"\right)",
                "=",
                syt(q),
                r"\odot \left(",
                syt(b),
                syt(g_sym),
                r"\right)",
            ],
        )
    )
    dd_num = c.T * d_num
    doc.append(
        tex.Math(
            data=[
                syt(dd_sym),
                "=",
                syt(dd_num),
                "=",
                syt(c.T),
                syt(d_num),
                "=",
                syt(c.T),
                syt(d_sym),
            ]
        )
    )
    ss_num = sy.hadamard_product(gg_num, dd_num)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(ss_sym),
                "=",
                syt(ss_num),
                "=",
                syt(gg_num),
                r"\odot",
                syt(dd_num),
                "=",
                syt(gg_sym),
                r"\odot",
                syt(dd_sym),
            ],
        )
    )
    s_num = a.T * ss_num
    doc.append(
        tex.Math(
            data=[
                syt(s_sym),
                "=",
                syt(s_num),
                "=",
                syt(a.T),
                syt(ss_num),
                "=",
                syt(a.T),
                syt(ss_sym),
            ]
        )
    )
    doc.append(
        tex.Math(data=[r"a^{t} =", syt(fast.matrix_to_log2(a.T))], escape=False)
    )
    doc.append(
        tex.Math(data=[r"b =", syt(fast.matrix_to_log2(b))], escape=False)
    )
    doc.append(
        tex.Math(data=[r"c^{t} =", syt(fast.matrix_to_log2(c.T))], escape=False)
    )
    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)

    output_default = signal.convolve(d_num, g_num[::-1, ::-1], mode="valid")
    compare_naive = np.all(
        output_default.reshape(-1) == np.array(s_num).reshape(-1)
    )
    print("Result:", compare_naive)


def example_2d_bind_nest(init_data, build_data, d1_user, g1_user, path):
    dim, c_len, b_len, a_len = init_data
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    d1_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"d_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
        ),
    )

    d2_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(
                f"\\delta_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0])
            )
        ),
    )
    dd_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"D_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
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
        b2.shape[1],
        sy.symbols(
            " ".join(
                f"\\gamma_{{{i}}}" for i in range(b1.shape[1] * b2.shape[1])
            )
        ),
    )
    gg_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"G_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
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

    doc = tex.Document()
    doc.preamble.append(tex.Package("geometry", "a1paper"))
    doc.preamble.append(tex.Command("title", "Numeric Nested 2D Convolution"))
    doc.preamble.append(
        tex.Command("author", "Fast-Convolution Python Library")
    )
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))
    doc.append(
        tex.Math(
            escape=False,
            data=[
                r"s=a_1^t \{[(q_1 \odot b_1) g (q_2 \odot b_2)^t] \odot (c_1^t d c_2)\}a_2"
            ],
        )
    )
    doc.append(
        tex.Math(data=["d =", syt(d1_sym), "=", syt(d1_user)], escape=False)
    )
    doc.append(
        tex.Math(data=["g =", syt(g1_sym), "=", syt(g1_user)], escape=False)
    )
    doc.append(
        tex.Math(
            data=[r"G = (q_1 \odot b_1) g (q_2 \odot b_2)^t"], escape=False
        )
    )
    g_num2 = sy.Matrix(g1_user) * (sy.diag(*q1) * b1).T
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(g2_sym),
                "=",
                syt(g_num2),
                "=",
                syt(g1_sym),
                r"\odot",
                syt((sy.diag(*q1) * b1).T),
                "=",
                syt(g1_sym),
                r"\left(",
                syt(q1),
                r"\odot",
                syt(b1),
                r"\right)^t",
            ],
        )
    )

    gg_num = sy.diag(*q2) * b2 * sy.Matrix(g_num2)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(gg_sym),
                "=",
                syt(gg_num),
                "=",
                syt(sy.diag(*q2) * b2),
                r"\odot",
                syt(g2_sym),
                r"= \left(",
                syt(q2),
                r"\odot",
                syt(b2),
                r"\right)",
                syt(g2_sym),
            ],
        )
    )

    doc.append(tex.Math(data=[r"D = c_1^t d c_2"], escape=False))
    d_num2 = d1_user * c2
    doc.append(
        tex.Math(
            data=[
                syt(d2_sym),
                "=",
                syt(d_num2),
                "=",
                syt(d1_user),
                syt(c2),
                "=",
                syt(d1_sym),
                syt(c2),
            ],
            escape=False,
        )
    )
    dd_num = c1.T * d_num2
    doc.append(
        tex.Math(
            data=[syt(dd_sym), "=", syt(dd_num), "=", syt(c1.T), syt(d2_sym)],
            escape=False,
        )
    )

    doc.append(tex.Math(data=[r"S = G \odot D"], escape=False))
    ss_num2 = sy.hadamard_product(gg_num, dd_num)
    doc.append(
        tex.Math(
            data=[
                syt(ss2_sym),
                "=",
                syt(ss_num2),
                "=",
                syt(gg_num),
                r"\odot",
                syt(dd_num),
            ],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"s = a_1^t S a_2"], escape=False))
    ss_num1 = ss_num2 * a2
    doc.append(
        tex.Math(
            data=[
                syt(ss1_sym),
                "=",
                syt(ss_num1),
                "=",
                syt(ss_num2),
                syt(a2),
                "=",
                syt(ss2_sym),
                syt(a2),
            ],
            escape=False,
        )
    )
    s_num = a1.T * ss_num1
    doc.append(
        tex.Math(
            data=[
                syt(s_sym),
                "=",
                syt(s_num),
                "=",
                syt(a1.T),
                syt(ss_num1),
                "=",
                syt(a1.T),
                syt(ss1_sym),
            ],
            escape=False,
        )
    )
    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)

    output_default = default_convolve(d1_user, g1_user)
    compare_naive = np.all(
        output_default.reshape(-1) == np.array(s_num).reshape(-1)
    )
    print("Result:", compare_naive)


def example_2d_bind_kron(init_data, build_data, d1_user, g1_user, path):
    dim, c_len, b_len, a_len = init_data
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
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"G_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
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
        c1.T.shape[0],
        c2.T.shape[0],
        sy.symbols(
            " ".join(f"D_{{{i}}}" for i in range(c1.T.shape[0] * c2.T.shape[0]))
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

    doc = tex.Document()
    doc.preamble.append(tex.Package("geometry", "a0paper"))
    doc.preamble.append(
        tex.Command("title", "Symbolic 2D Kronecker Convolution")
    )
    doc.preamble.append(
        tex.Command("author", "Fast-Convolution Python Library")
    )
    doc.preamble.append(tex.Command("date", tex.NoEscape(r"\today")))
    doc.append(tex.NoEscape(r"\maketitle"))

    doc.append(
        tex.Math(
            escape=False,
            data=[
                r"s=(a_1^t \otimes a_2^t) \{[(q_1 \odot b_1) g (q_2 \odot b_2)^t] \odot (c_1^t \otimes c_2^t)\} d"
            ],
        )
    )
    doc.append(
        tex.Math(data=["d =", syt(d_sym), "=", syt(d1_user)], escape=False)
    )
    doc.append(
        tex.Math(data=["g =", syt(g1_sym), "=", syt(g1_user)], escape=False)
    )
    doc.append(
        tex.Math(
            data=[r"G = (q_1 \odot b_1) g (q_2 \odot b_2)^t"], escape=False
        )
    )
    g2_num = sy.Matrix(g1_user) * (sy.diag(*q1) * b1).T
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(g2_sym),
                "=",
                syt(g2_num),
                "=",
                syt(g1_user),
                r"\odot",
                syt((sy.diag(*q1) * b1).T),
                "=",
                syt(g1_sym),
                r"\left(",
                syt(q1),
                r"\odot",
                syt(b1),
                r"\right)^t",
            ],
        )
    )
    gg_num = sy.diag(*q2) * b2 * sy.Matrix(g2_num)
    doc.append(
        tex.Math(
            escape=False,
            data=[
                syt(gg_sym),
                "=",
                syt(gg_num),
                "=",
                syt(sy.diag(*q2) * b2),
                r"\odot",
                syt(g2_num),
                r"= \left(",
                syt(q2),
                r"\odot",
                syt(b2),
                r"\right)",
                syt(g2_sym),
            ],
        )
    )
    doc.append(tex.Math(data=[r"C = c_1^t \otimes c_2^t"], escape=False))
    cc_num = TensorProduct(c1.T, c2.T)
    doc.append(
        tex.Math(
            data=["C =", syt(cc_num), "=", syt(c1.T), r"\otimes", syt(c2.T)],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"A = a_1^t \otimes a_2^t"], escape=False))
    aa_num = TensorProduct(a1.T, a2.T)
    doc.append(
        tex.Math(
            data=["A =", syt(aa_num), "=", syt(a1.T), r"\otimes", syt(a2.T)],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"D = Cd"], escape=False))
    dd_num = cc_num * d1_user.reshape(cc_num.shape[1], 1)
    doc.append(
        tex.Math(
            data=[
                syt(dd_sym.reshape(dd_num.shape[0] * dd_num.shape[1], 1)),
                "=",
                syt(dd_num),
                "=",
                syt(cc_num),
                syt(d1_user.reshape(cc_num.shape[1], 1)),
            ]
        )
    )
    doc.append(tex.Math(data=[r"S = G \odot D"], escape=False))
    ss_num = sy.hadamard_product(
        gg_num, dd_num.reshape(gg_num.shape[0], gg_num.shape[1])
    )
    doc.append(
        tex.Math(
            data=[
                syt(ss_sym),
                "=",
                syt(ss_num),
                "=",
                syt(gg_num),
                r"\odot",
                syt(dd_num.reshape(gg_num.shape[0], gg_num.shape[1])),
            ],
            escape=False,
        )
    )
    doc.append(tex.Math(data=[r"s = AS"], escape=False))
    s_num = aa_num * ss_num.reshape(ss_num.shape[0] * ss_num.shape[1], 1)
    doc.append(
        tex.Math(
            data=[
                syt(s_sym.reshape(s_num.shape[0] * s_num.shape[1], 1)),
                "=",
                syt(s_num),
                "=",
                syt(aa_num),
                syt(ss_num.reshape(ss_num.shape[0] * ss_num.shape[1], 1)),
            ]
        )
    )

    doc.append(
        tex.Math(data=[r"A =", syt(fast.matrix_to_log2(aa_num))], escape=False)
    )
    doc.append(
        tex.Math(
            data=[r"C =", syt(fast.matrix_to_log2(cc_num.T))], escape=False
        )
    )

    try:
        doc.generate_pdf(path, clean_tex=False)
    except Exception as e:
        click.echo(e)

    output_default = signal.convolve(d1_user, g1_user[::-1, ::-1], mode="valid")
    compare_naive = np.all(
        output_default.reshape(-1) == np.array(s_num).reshape(-1)
    )
    print("Result:", compare_naive)
