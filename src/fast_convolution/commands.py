import os
import json
from pathlib import Path

import click
import numpy as np
import sympy as sy
from PIL import Image
from scipy import signal
from sklearn import metrics
# from matplotlib import pyplot as plt

from . import fast
from .naive import naive_convolve


root_path = Path(os.getcwd())
config_dir = root_path / "config"
init_file = config_dir / "init.json"
build_file = config_dir / "build.json"
build_dir = root_path / "build"
quant_dir = root_path / "quant"
sim_dir = root_path / "sim"


def read_init():
    with open(init_file) as f:
        data = json.load(f)
    c = data["c"]
    a = data["a"]
    b = data["b"]
    dim = data["dim"]
    return dim, c, b, a


def read_build():
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


def read_init_if_exists():
    if init_file.exists() is False:
        return None
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
    write_latex_image(b, c, a, bg, di, build_dir)
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

    path1 = build_dir / "1"
    path1.mkdir(parents=True, exist_ok=True)
    write_latex_image(b1, c1, a1, bg1, di1, path1)
    path2 = build_dir / "2"
    path2.mkdir(parents=True, exist_ok=True)
    write_latex_image(b2, c2, a2, bg2, di2, path2)
    click.echo("Build ok")


def write_latex_image(b, c, a, bg, di, path):
    bs = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b.shape[1]))))
    bgs = sy.Matrix(sy.symbols(" ".join(f"G_{i}"for i in range(b.shape[0]))))
    bg_step = fast.conv_step(bgs, b, bs)

    cs = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c.T.shape[0]))))
    cds = sy.Matrix(sy.symbols(" ".join(f"D_{i}"for i in range(c.T.shape[1]))))
    cd_step = fast.conv_step(cds, c.T, cs)

    s_small = sy.Matrix(sy.symbols(" ".join(f"S_{i}"for i in range(a.T.shape[0]))))
    s_big = sy.Matrix(sy.symbols(" ".join(f"s_{i}"for i in range(a.T.shape[1]))))
    s_step = fast.conv_step(s_small, a.T, s_big)

    mul = sy.MatMul(a.T, bg, c.T, di)
    sy.preview(
        sy.Eq(s_small, mul), viewer='file',
        filename=f'{path}/matrix_mult.png', euler=False
    )
    sy.preview(
        bg_step, viewer='file', filename=f'{path}/step_g.png', euler=False
    )
    sy.preview(
        cd_step, viewer='file', filename=f'{path}/step_d.png', euler=False
    )
    sy.preview(
        s_step, viewer='file', filename=f'{path}/step_s.png', euler=False
    )

    log2_at = sy.Eq(
        sy.MatrixSymbol('a', 2, 2).T, fast.matrix_to_log2(a.T), evaluate=False
    )
    log2_ct = sy.Eq(
        sy.MatrixSymbol('c', 2, 2).T, fast.matrix_to_log2(c.T), evaluate=False
    )
    sy.preview(
        log2_at, viewer='file', filename=f'{path}/log2_at.png', euler=False
    )
    sy.preview(
        log2_ct, viewer='file', filename=f'{path}/log2_ct.png', euler=False
    )


def cmd_iterate2d():
    dim, c_len, b_len, a_len = read_init()
    d1 = sy.Matrix(
        c_len, c_len,
        sy.symbols(" ".join(f"d_{i}"for i in range(c_len **2)))
    )
    g1 = sy.Matrix(
        c_len, c_len,
        sy.symbols(" ".join(f"g_{i}"for i in range(c_len **2)))
    )
    dd = sy.symbol("D")
    gg = sy.symbol("G")

    build_data = read_build()
    p1, p2 = build_data["p"]
    c1 = sy.Matrix(build_data["c"][0])
    c2 = sy.Matrix(build_data["c"][1])
    q1, q2 = build_data["q"]
    b1 = sy.Matrix(build_data["b"][0])
    b2 = sy.Matrix(build_data["b"][1])
    a1 = (build_data["a"][0])
    a2 = (build_data["a"][1])

    d1s = sy.MatrixSymbol('d', 2, 2)
    gs = sy.MatrixSymbol('g', 2, 2)
    a1s = sy.MatrixSymbol('a_1', 2, 2)
    a2s = sy.MatrixSymbol('a_2', 2, 2)
    b1s = sy.MatrixSymbol('b_1', 2, 2)
    b2s = sy.MatrixSymbol('b_2', 2, 2)
    c1s = sy.MatrixSymbol('c_1', 2, 2)
    c2s = sy.MatrixSymbol('c_2', 2, 2)

    d2s = c1s.T * d1s * c2s
    step_d1a = sy.Eq(d1*c2, sy.MatMul(d1, c2, evaluate=False))
    step_d1b = sy.Eq(c1.T*d1*c2, step_d1a)
    step_d1c = sy.Eq(d2s, step_d1b)
    step_d2 = sy.Eq(dd, step_d1c)
    path = build_dir / "bind"
    path.mkdir(parents=True, exist_ok=True)
    sy.preview(
        step_d2, viewer='file', filename=f'{path}/step_d.png', euler=False
    )




def cmd_sim_file(feature, weight):
    dim, c_len, b_len, a_len = read_init()
    points, c, b, a, q = read_build()

    # with open('quant.json') as f:
    #     quant_file = json.load(f)

    # constant = quant_file["const"]
    integer = False

    with open(feature) as f:
        image = Image.open(feature).convert('L')
        feat_arr = np.array(image)
    with open(weight) as f:
        wght_arr = (np.array(json.load(f)).reshape(b_len, b_len))

    fast_conv = [
        fast.conv1d(
            wght_arr[i], c, q, b, a, type_int=integer
        )
        for i in range(b_len)
    ]

    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode='valid'
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    print(
        f"Output default and naive are equals: {compare_naive}"
    )

    output_fast = np.sum(axis=0, a=[
        fast.filter1d_slide2d(
            fast_conv[i], feat_arr, output_default.shape, i, c_len,
            a_len
        )
        for i in range(0, wght_arr.shape[0])
     ])

    if integer:
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

    click.echo("Naive totals:")
    click.echo(f"Iterations: {size}")
    click.echo(f"Multiplications: {size * 9}")
    click.echo(f"Additions: {size * 8}")

    click.echo("Fast totals:")
    fast_count = fast.filter1d_slide2d_count(output_default.shape, a_len)
    mult = fast_count * len(points) * len(fast_conv)
    click.echo(f"Iterations: {fast_count}")
    click.echo(f"Multiplications: {mult}")
    add0 = fast_count * 20 * len(fast_conv)
    add1 = fast_count * 2 * len(fast_conv)
    click.echo(f"Additions: {add0 + add1}")
    click.echo(f"* Additions for each batch processed: {add0}")
    click.echo(f"* Additions to join batches: {add1}")
    click.echo(
        f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
    )


def cmd_sim_random(feature_random, weight_random, image_side, integer, loop):
    with open('init.json') as f:
        init_file = json.load(f)
    init = read_init(init_file)
    m_size, n_size, points, c, b, a, q = init

    feat = np.random.randint(
         feature_random[0], feature_random[1], size=image_side ** 2
     )
    wght = np.random.randint(
        weight_random[0], weight_random[1], size=n_size ** 2
    )
    feat_arr = feat.reshape(image_side, image_side)
    wght_arr = wght.reshape(n_size, n_size)
    fast_conv = [
        fast.conv1d(
            wght_arr[i], c, q, b, a, type_int=integer
        )
        for i in range(n_size)
    ]

    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode='valid'
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    click.echo(
        f"Output default and naive are equals: {compare_naive}"
    )

    output_fast = np.sum(axis=0, a=[
        fast.filter1d_slide2d(
            fast_conv[i], feat_arr, output_default.shape, i, len(points),
            m_size
        )
        for i in range(0, wght_arr.shape[0])
     ])

    if integer:
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

    click.echo("Naive totals:")
    click.echo(f"Iterations: {size}")
    click.echo(f"Multiplications: {size * 9}")
    click.echo(f"Additions: {size * 8}")

    click.echo("Fast totals:")

    fast_count = fast.filter1d_slide2d_count(output_default.shape, m_size)
    mult = fast_count * len(points) * len(fast_conv)
    click.echo(f"Iterations: {fast_count}")
    click.echo(f"Multiplications: {mult}")

    add0 = fast_count * 20 * len(fast_conv)
    add1 = fast_count * 2 * len(fast_conv)

    click.echo(f"Additions: {add0 + add1}")
    click.echo(f"* Additions for each batch processed: {add0}")
    click.echo(f"* Additions to join batches: {add1}")
    click.echo(
        f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
    )

