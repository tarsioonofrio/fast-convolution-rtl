import os
import json
from pathlib import Path

import click
import numpy as np
import sympy as sy
import pylatex as tex
from PIL import Image
from scipy import signal
from sklearn import metrics
# from matplotlib import pyplot as plt

from . import fast
from . import quant
from .naive import naive_convolve


root_path = Path(os.getcwd())
config_dir = root_path / "config"
init_file = config_dir / "init.json"
build_file = config_dir / "build.json"
quant_file = config_dir / "quant.json"
build_dir = root_path / "build"
quant_dir = root_path / "quant"
example_dir = root_path / "example"
sim_dir = root_path / "sim"


def read_init():
    with open(init_file) as f:
        data = json.load(f)
    c = data["c"]
    a = data["a"]
    b = data["b"]
    dim = data["dim"]
    return dim, c, b, a


def read_build_1d():
    with open(build_file) as f:
        data = json.load(f)
    p = data["p"]
    c = sy.Matrix(data["c"])
    b = sy.Matrix(data["b"])
    a = sy.Matrix(data["a"])
    q = sy.Matrix([
        sy.Rational(p, q) for p, q in data["q"]
    ])
    return p, c, b, a, q


def read_build_2d():
    with open(build_file) as f:
        data = json.load(f)
    p = sy.Matrix(data["p"][0]), sy.Matrix(data["p"][1])
    c = sy.Matrix(data["c"][0]), sy.Matrix(data["c"][1])
    b = sy.Matrix(data["b"][0]), sy.Matrix(data["b"][1])
    a = sy.Matrix(data["a"][0]), sy.Matrix(data["a"][1])
    q = [
        sy.Matrix([sy.Rational(p, q) for p, q in d])
        for d in data["q"]
    ]
    return p, c, b, a, q


def read_init_if_exists():
    if init_file.exists() is False:
        return {}
    with open(init_file) as f:
        data = json.load(f)
    return data


def read_num_points():
    if init_file.exists() is False:
        return 1
    dim, c, b, a = read_init()
    return c


def num_points1d(size):
    if isinstance(size, int):
        return size
    else:
        return 1


def num_points2d(size, axis):
    if isinstance(size, list) is False:
        return 1
    return size[axis]


def default_toom_cook_points1d(size):
    if isinstance(size, int) is False:
        return 1
    p0 = [p*s for s in range(1, size//2 + size % 2) for p in [1, -1]]
    p = [0] + p0[:size-1 - size % 2] + ['inf']
    return p


def default_toom_cook_points2d(size0, axis=None):
    if isinstance(size0, list) is False:
        return 1
    size = size0[axis]
    p0 = [p*s for s in range(1, size//2 + size % 2) for p in [1, -1]]
    p = [0] + p0[:size-1 - size % 2] + ['inf']
    return p


def read_quant_if_exists():
    if quant_file.exists() is False:
        return {}
    with open(quant_file) as f:
        data = json.load(f)
    return data


def syt(expr):
    return tex.NoEscape(sy.latex(expr)) 


def cmd_init(dimensions, in_len, out_len, w):
    if init_file.exists():
        click.echo(
            message="init.json existis, fconv model already initialized"
        )
        click.Abort()
        exit(1)
    in_arr = np.array(in_len)
    w_arr = np.array(w)
    out_arr = np.array(out_len)
    if in_len is None and out_len is None:
        b = in_arr - out_arr + 1
        c = in_arr
        a = out_arr
    elif in_len is None:
        c = out_arr + w_arr - 1
        a = out_arr
        b = w_arr
    elif out_len is None:
        a = in_arr - w_arr + 1
        c = in_arr
        b = w_arr
    else:
        click.echo(
            message="Just one param is passed, inform another."
        )
        click.Abort()
        exit(1)

    data = {
        "dim": dimensions,
        "c": c.tolist(),
        "a": a.tolist(),
        "b": b.tolist(),
    }
    init_file.parent.mkdir(parents=True, exist_ok=True)
    with open(init_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    click.echo("Init ok")


def cmd_show(init, build, quant):
    init_data = read_init_if_exists()
    if init_file.exists():
        if init:
            click.echo(read_init_if_exists())
        if build and build_file.exists():
            if init_data["dim"] == 1:
                click.echo(read_build_1d())
            elif init_data["dim"] == 2:
                click.echo(read_build_2d())
        if quant and quant_file.exists():
            click.echo(read_quant_if_exists())


def cmd_build_toom_cook1d(points):
    dim, c_len, b_len, a_len = read_init()
    # at_len = ct_len + b_len - 1
    list_points = [np.inf if p == 'inf' else int(p) for p in points]

    c, q, b, a = fast.toom_cook(a_len, b_len, list_points)
    di = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c_len))))
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b_len))))
    bg = fast.g_to_bg(q, b, g)
    qr = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q
    ]
    data = {
        "p": list_points,
        "c": np.array(c, dtype=int).tolist(),
        "q": qr,
        "b": np.array(b, dtype=int).tolist(),
        "a": np.array(a, dtype=int).tolist(),
    }
    with open(build_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    build_dir.mkdir(parents=True, exist_ok=True)
    save_build_pdf(b, c, a, bg, di, build_dir / "convolution")
    click.echo("Build ok")


def cmd_build_toom_cook2d(points1d, points2d):
    dim, c_len, b_len, a_len = read_init()
    # at_len = ct_len + b_len - 1
    list_points1d = [np.inf if p == 'inf' else int(p) for p in points1d]
    list_points2d = [np.inf if p == 'inf' else int(p) for p in points2d]

    c1, q1, b1, a1 = fast.toom_cook(a_len[0], b_len[0], list_points1d)
    di1 = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c_len[0]))))
    g1 = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b_len[0]))))
    bg1 = fast.g_to_bg(q1, b1, g1)
    qr1 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q1
    ]

    c2, q2, b2, a2 = fast.toom_cook(a_len[1], b_len[1], list_points2d)
    di2 = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c_len[1]))))
    g2 = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b_len[1]))))
    bg2 = fast.g_to_bg(q2, b2, g2)
    qr2 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q2
    ]

    data = {
        "p": [list_points1d, list_points2d],
        "c": [np.array(c1, dtype=int).tolist(), np.array(c2, dtype=int).tolist()],
        "q": [qr1, qr2],
        "b": [np.array(b1, dtype=int).tolist(), np.array(b2, dtype=int).tolist()],
        "a": [np.array(a1, dtype=int).tolist(), np.array(a2, dtype=int).tolist()],
    }
    with open(build_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    build_dir.mkdir(parents=True, exist_ok=True)
    path1 = build_dir / "convolution-axis1"
    save_build_pdf(b1, c1, a1, bg1, di1, path1)
    path2 = build_dir / "convolution-axis2"
    save_build_pdf(b2, c2, a2, bg2, di2, path2)
    click.echo("Build ok")


def save_build_pdf(b, c, a, bg, di, path):
    bs = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b.shape[1]))))
    bgs = sy.Matrix(sy.symbols(" ".join(f"G_{i}"for i in range(b.shape[0]))))

    cs = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c.T.shape[0]))))
    cds = sy.Matrix(sy.symbols(" ".join(f"D_{i}"for i in range(c.T.shape[1]))))

    s_big = sy.Matrix(sy.symbols(" ".join(f"S_{i}"for i in range(a.T.shape[1]))))
    s_small = sy.Matrix(sy.symbols(" ".join(f"s_{i}"for i in range(a.T.shape[0]))))

    mul = sy.MatMul(a.T, bg, c.T, di)

    doc = tex.Document()
    doc.preamble.append(tex.Package('geometry', 'a3paper'))
    doc.preamble.append(tex.Command('title', 'Symbolic 1D Convolution'))
    doc.preamble.append(tex.Command('author', 'Fast-Convolution Python Library'))
    doc.preamble.append(tex.Command('date', tex.NoEscape(r'\today')))
    doc.append(tex.NoEscape(r'\maketitle'))

    doc.append(
        tex.Math(data=[r"s = a^t {(bg) \odot (c^t d)}"], escape=False)
    )

    doc.append(
        tex.Math(data=[syt(s_small), "=", syt(mul)])
    )
    doc.append(
        tex.Math(data=[
            syt(bgs), "=", syt(b*bs), "=", syt(b),
            syt(bs)
        ])
    )
    doc.append(
        tex.Math(data=[
            syt(cds), "=", syt(c.T*cs), "=", syt(c.T),
            syt(cs)
        ])
    )
    doc.append(
        tex.Math(data=[
            syt(s_small), "=", syt(a.T*s_big), "=", syt(a.T),
            syt(s_big)
        ])
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

    doc.generate_pdf(path, clean_tex=False)


def save_example_pdf(b, c, a, bg, d, g, q, path):
    # g = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b.shape[1]))))
    gg = sy.Matrix(sy.symbols(" ".join(f"G_{i}"for i in range(b.shape[0]))))

    # d = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c.T.shape[0]))))
    dd = sy.Matrix(sy.symbols(" ".join(f"D_{i}"for i in range(c.T.shape[1]))))

    s_big = sy.Matrix(sy.symbols(" ".join(f"S_{i}"for i in range(a.T.shape[1]))))
    s_small = sy.Matrix(sy.symbols(" ".join(f"s_{i}"for i in range(a.T.shape[0]))))
    # breakpoint()
    bgs = sy.hadamard_product(q, sy.MatMul(b, g))

    mul = sy.MatMul(a.T, bg, c.T, d)

    doc = tex.Document()
    doc.preamble.append(tex.Package('geometry', 'a3paper'))
    doc.preamble.append(tex.Command('title', 'Numeric 1D Convolution'))
    doc.preamble.append(tex.Command('author', 'Fast-Convolution Python Library'))
    doc.preamble.append(tex.Command('date', tex.NoEscape(r'\today')))
    doc.append(tex.NoEscape(r'\maketitle'))

    doc.append(
        tex.Math(data=[r"s = a^t {(bg) \odot (c^t d)}"], escape=False)
    )

    doc.append(
        tex.Math(escape=False, data=[
            syt(s_small), "=", syt(a.T), r"\left[",syt(q), r"\odot \left(", syt(b), syt(g), r"\right)\right]",syt(d)
        ])
    )
    doc.append(
        tex.Math(data=[
            syt(gg), "=", syt(b*g), "=", syt(b),
            syt(g)
        ])
    )
    doc.append(
        tex.Math(data=[
            syt(dd), "=", syt(c.T*d), "=", syt(c.T),
            syt(d)
        ])
    )
    doc.append(
        tex.Math(data=[
            syt(s_small), "=", syt(a.T*s_big), "=", syt(a.T),
            syt(s_big)
        ])
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

    doc.generate_pdf(path, clean_tex=False)


def cmd_iterate2d():
    dim, c_len, b_len, a_len = read_init()
    with open(build_file) as f:
        build_data = json.load(f)

    p1, p2 = build_data["p"]
    c1 = sy.Matrix(build_data["c"][0])
    c2 = sy.Matrix(build_data["c"][1])
    q1, q2 = build_data["q"]
    b1 = sy.Matrix(build_data["b"][0])
    b2 = sy.Matrix(build_data["b"][1])
    a1 = sy.Matrix(build_data["a"][0])
    a2 = sy.Matrix(build_data["a"][1])

    d1 = sy.Matrix(
        c_len[0], c_len[0],
        sy.symbols(" ".join(f"d_{i}"for i in range(c_len[0] * c_len[1])))
    )
    d2 = sy.Matrix(
        c_len[0], c_len[0],
        sy.symbols(" ".join(f"\\delta_{{{i}}}"for i in range(c_len[0] * c_len[1])))
    )
    dd = sy.Matrix(
        c_len[0], c_len[0],
        sy.symbols(" ".join(f"D_{{{i}}}"for i in range(c_len[0] * c_len[1])))
    )
    g1 = sy.Matrix(
        b_len[0], b_len[0],
        sy.symbols(" ".join(f"g_{{{i}}}"for i in range(b_len[0] * b_len[1])))
    )
    g2 = sy.Matrix(
        b_len[0], c_len[0],
        sy.symbols(" ".join(f"\\gamma_{{{i}}}"for i in range(b_len[0] * c_len[0])))
    )
    gg = sy.Matrix(
        c_len[0], c_len[0],
        sy.symbols(" ".join(f"G_{{{i}}}"for i in range(c_len[0] * c_len[1])))
    )
    s2 = sy.Matrix(
        c_len[0], c_len[0],
        sy.symbols(" ".join(f"S_{{{i}}}"for i in range(c_len[0] * c_len[1])))
    )
    s1 = sy.Matrix(
        c_len[0], b_len[0],
        sy.symbols(" ".join(f"\\sigma_{{{i}}}"for i in range(b_len[0] * c_len[0])))
    )
    s = sy.Matrix(
        a_len[0], a_len[0],
        sy.symbols(" ".join(f"s_{{{i}}}"for i in range(b_len[0] * b_len[1])))
    )

    doc = tex.Document()
    doc.preamble.append(tex.Package('geometry', 'a1paper'))
    doc.preamble.append(tex.Command('title', 'Iterated 2D Convolution'))
    doc.preamble.append(tex.Command('author', 'Fast-Convolution Python Library'))
    doc.preamble.append(tex.Command('date', tex.NoEscape(r'\today')))
    doc.append(tex.NoEscape(r'\maketitle'))
    doc.append(
        tex.Math(data=["s=a_1^t [(b_1 g b_2^t) \odot (c_1^t d c_2)]a _2"], escape=False)
    )

    doc.append(
        tex.Math(data=[r"G = b_1 g b_2^t"], escape=False)
    )
    doc.append(
        tex.Math(data=[
            syt(g2), "=", syt(g1 * b2.T), "=", syt(g1),
            syt(b2.T)
        ], escape=False)
    )
    doc.append(
        tex.Math(data=[
            syt(gg), "=", syt(b1 * g2), "=", syt(b1),
            syt(g2)
        ], escape=False)
    )

    doc.append(
        tex.Math(data=[r"D = c_1^t d c_2"], escape=False)
    )
    doc.append(
        tex.Math(data=[
            syt(d2), "=", syt(d1 * c2), "=", syt(d1),
            syt(c2)
        ], escape=False)
    )
    doc.append(
        tex.Math(data=[
            syt(dd), "=", syt(c1.T * d2), "=", syt(c1.T),
            syt(d2)
        ], escape=False)
    )

    doc.append(
        tex.Math(data=[r"S = G \odot D"], escape=False)
    )
    doc.append(
        tex.Math(data=[r"s = a_1^t S a_2"], escape=False)
    )
    doc.append(
        tex.Math(data=[
            syt(s1), "=", syt(s2 * a2), "=", syt(s2),
            syt(a2)
        ], escape=False)
    )
    doc.append(
        tex.Math(data=[
            syt(s), "=", syt(a1.T * s1), "=", syt(a1.T),
            syt(s1)
        ], escape=False)
    )
    path = build_dir / "bind"
    doc.generate_pdf(path, clean_tex=False)


def cmd_quant_none():
    quant_file.unlink(missing_ok=True)


def cmd_quant_shift(bits):
    data = {
        "func": "shift",
        "params": {
            "bits": bits
        }
    }
    with open(quant_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def cmd_sim_file(feature, weight):
    dim, c_len, b_len, a_len = read_init()
    quant_data = read_quant_if_exists()
    with open(feature) as f:
        image = Image.open(feature).convert('L')
        feat_arr = np.array(image)
    with open(weight) as f:
        if dim == 1:
            wght_arr = (np.array(json.load(f)).reshape(b_len, b_len))
        elif dim == 2:
            wght_arr = (np.array(json.load(f)).reshape(b_len[0], b_len[1]))

    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode='valid'
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    print(
        f"Output default and naive are equals: {compare_naive}"
    )

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        conv_func = (
            fast.conv1d if len(quant_data) == 0
            else quant.select_func1d(quant_data)
        )
        fast_conv = [
            conv_func(
                wght_arr[i], c, q, b, a
            )
            for i in range(b_len)
        ]

        output_fast = np.sum(axis=0, a=[
            fast.filter1d_slide2d(
                fast_conv[i], feat_arr, output_default.shape, i, c_len,
                a_len
            )
            for i in range(0, wght_arr.shape[0])
         ])
        count_iter = fast.filter1d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points) * len(fast_conv)
    elif dim == 2:
        points, c, b, a, q = read_build_2d()
        conv_func = (
            fast.conv2d if len(quant_data) == 0
            else quant.select_func2d(quant_data)
        )
        fast_conv = conv_func(
            wght_arr, c[0], q[0], b[0], a[0], c[1], q[1], b[1], a[1]
        )
        output_fast = fast.filter2d_slide2d(
            fast_conv, feat_arr, output_default.shape, c_len, a_len
        )
        count_iter = fast.filter2d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points[0]) * len(points[1])

    if len(quant_data) != 0:
        rmse = metrics.root_mean_squared_error(
            output_default.reshape(-1), output_fast.reshape(-1)
        )
        mae = metrics.mean_absolute_error(
            output_default.reshape(-1), output_fast.reshape(-1)
        )
        click.echo(f"RMSE : {rmse}")
        click.echo(f"MAE : {mae}")
    else:
        compare_fast = np.all(output_default == output_fast)
        click.echo(
            f"Output default and fast are equals: {compare_fast}"
        )

    size = output_default.size

    click.echo("Totals")
    click.echo("Naive")
    click.echo(f"Convolutions: {size}")
    click.echo(f"Multiplications: {size * 9}")
    click.echo(f"Additions: {size * 8}")

    click.echo("Fast")
    click.echo(f"Convolutions: {count_iter}")
    click.echo(f"Multiplications: {count_mult}")
    # add0 = fast_count * 20 * len(fast_conv)
    # add1 = fast_count * 2 * len(fast_conv)
    # click.echo(f"Additions: {add0 + add1}")
    # click.echo(f"* Additions for each batch processed: {add0}")
    # click.echo(f"* Additions to join batches: {add1}")
    # click.echo(
    #     f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
    # )


def cmd_sim_random(feature_random, weight_random, image_side, integer, loop):
    dim, c_len, b_len, a_len = read_init()
    quant_data = read_quant_if_exists()
    feat = np.random.randint(
         feature_random[0], feature_random[1], size=image_side ** 2
     )
    feat_arr = feat.reshape(image_side, image_side)

    if dim == 1:
        wght = np.random.randint(
            weight_random[0], weight_random[1], size=b_len ** 2
        )
        wght_arr = wght.reshape(b_len, b_len)
    elif dim == 2:
        wght = np.random.randint(
            weight_random[0], weight_random[1],
            size=b_len[0] * b_len[1]
        )
        wght_arr = wght.reshape(b_len[0], b_len[1])

    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode='valid'
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    print(
        f"Output default and naive are equals: {compare_naive}"
    )

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        conv_func = (
            fast.conv1d if len(quant_data) == 0
            else quant.select_func1d(quant_data)
        )
        fast_conv = [
            conv_func(
                wght_arr[i], c, q, b, a
            )
            for i in range(b_len)
        ]

        output_fast = np.sum(axis=0, a=[
            fast.filter1d_slide2d(
                fast_conv[i], feat_arr, output_default.shape, i, c_len,
                a_len
            )
            for i in range(0, wght_arr.shape[0])
         ])
        count_iter = fast.filter1d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points) * len(fast_conv)
    elif dim == 2:
        points, c, b, a, q = read_build_2d()
        conv_func = (
            fast.conv2d if len(quant_data) == 0
            else quant.select_func2d(quant_data)
        )
        fast_conv = conv_func(
            wght_arr, c[0], q[0], b[0], a[0], c[1], q[1], b[1], a[1]
        )
        output_fast = fast.filter2d_slide2d(
            fast_conv, feat_arr, output_default.shape, c_len, a_len
        )
        count_iter = fast.filter2d_slide2d_count(
            output_default.shape, a_len
        )
        count_mult = count_iter * len(points[0]) * len(points[1])

    if len(quant_data) != 0:
        rmse = metrics.root_mean_squared_error(
            output_default.reshape(-1), output_fast.reshape(-1)
        )
        mae = metrics.mean_absolute_error(
            output_default.reshape(-1), output_fast.reshape(-1)
        )
        click.echo(f"RMSE : {rmse}")
        click.echo(f"MAE : {mae}")
    else:
        compare_fast = np.all(output_default == output_fast)
        click.echo(
            f"Output default and fast are equals: {compare_fast}"
        )

    size = output_default.size

    click.echo("Totals:")
    click.echo("Naive:")
    click.echo(f"Convolutions: {size}")
    click.echo(f"Multiplications: {size * 9}")
    click.echo(f"Additions: {size * 8}")

    click.echo("Fast:")
    click.echo(f"Convolutions: {count_iter}")
    click.echo(f"Multiplications: {count_mult}")


def cmd_example(feature, weight):
    dim, c_len, b_len, a_len = read_init()

    if dim == 1:
        f = np.random.randint(
            feature[0], feature[1], size=c_len
        )
        d = sy.Matrix(f)
        w = np.random.randint(
            weight[0], weight[1], size=b_len
        )
        g = sy.Matrix(w)
    elif dim == 2:
        f0 = np.random.randint(
            feature[0], feature[1], size=c_len[0]*c_len[1]
        )
        f = np.array(f0).reshape(c_len[0], c_len[1])
        d = sy.Matrix(f)
        w0 = np.random.randint(
            weight[0], weight[1], size=b_len[0] * b_len[1]
        )
        w = np.array(w0).reshape(b_len[0], b_len[1])
        g = sy.Matrix(w)

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        bg = fast.g_to_bg(q, b, g)
        example_dir.mkdir(parents=True, exist_ok=True)
        save_example_pdf(b, c, a, bg, d, g, q, example_dir / "example")

    elif dim == 2:
        points, c, b, a, q = read_build_2d()




