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


# root = Path(__file__).resolve().parent
root_path = Path(os.getcwd())
config_path = root_path / "config"
init_file = config_path / "init.json"
build_file = config_path / "build.json"


def read_init():
    with open(init_file) as f:
        data = json.load(f)
    d = data["d"]
    m = data["m"]
    n = data["n"]
    return d, m, n


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


def read_num_points():
    if init_file.exists() is False:
        return 1
    d, m, n = read_init()
    p = m + n - 1
    return p


def cmd_init(dimensions, m, n):
    if init_file.exists():
        click.echo(
            message="init.json existis, fconv model already initialized"
        )
        click.Abort()
        exit(1)

    data = {
        "d": dimensions,
        "m": m,
        "n": n,
    }
    init_file.parent.mkdir(parents=True, exist_ok=True)
    with open(init_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    click.echo("Initialized")


def cmd_build_toom_cook(points):
    init_data = read_init()
    d_size, m_size, n_size = init_data
    i_size = m_size + n_size - 1
    list_points = [np.inf if p == 'inf' else int(p) for p in points]

    c, q, b, a = fast.toom_cook(m_size, n_size, list_points)
    di = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(i_size))))
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(n_size))))
    bg = fast.g_to_bg(q, b, g)
    q0 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q
    ]
    data = {
        "p": list_points,
        "m": m_size,
        "n": n_size,
        "c": np.array(c, dtype=int).tolist(),
        "q": q0,
        "b": np.array(b, dtype=int).tolist(),
        "a": np.array(a, dtype=int).tolist(),
    }
    with open(build_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    bs = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b.shape[1]))))
    bgs = sy.Matrix(sy.symbols(" ".join(f"G_{i}"for i in range(b.shape[0]))))
    bg_step = conv_step(bgs, b, bs)

    cs = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c.T.shape[0]))))
    cds = sy.Matrix(sy.symbols(" ".join(f"D_{i}"for i in range(c.T.shape[1]))))
    cd_step = conv_step(cds, c.T, cs)

    s_small = sy.Matrix(sy.symbols(" ".join(f"S_{i}"for i in range(a.T.shape[0]))))
    s_big = sy.Matrix(sy.symbols(" ".join(f"s_{i}"for i in range(a.T.shape[1]))))
    s_step = conv_step(s_small, a.T, s_big)

    # TODO export matrix form too
    mul = sy.MatMul(a.T, bg, c.T, di)
    sy.preview(
        sy.Eq(s_small, mul), viewer='file',
        filename='matrix_mult.png', euler=False
    )
    sy.preview(
        bg_step, viewer='file', filename='step_g.png', euler=False
    )
    sy.preview(
        cd_step, viewer='file', filename='step_d.png', euler=False
    )
    sy.preview(
        s_step, viewer='file', filename='step_s.png', euler=False
    )

    log2_at = sy.Eq(
        sy.MatrixSymbol('a', 2, 2).T, fast.matrix_to_log2(a.T), evaluate=False
    )
    log2_ct = sy.Eq(
        sy.MatrixSymbol('c', 2, 2).T, fast.matrix_to_log2(c.T), evaluate=False
    )
    sy.preview(
        log2_at, viewer='file', filename='log2_at.png', euler=False
    )
    sy.preview(
        log2_ct, viewer='file', filename='log2_ct.png', euler=False
    )


def cmd_sim_file(feature, weight):
    with open('init.json') as f:
        init_file = json.load(f)
        d, m_size, n_size = read_init(init_file)

    with open('build.json') as f:
        build_file = json.load(f)
        points, c, b, a, q = read_build(build_file)

    with open('quant.json') as f:
        quant_file = json.load(f)

    constant = quant_file["const"]
    integer = quant_file["integer"]

    with open(feature) as f:
        image = Image.open(feature).convert('L')
        feat_arr = np.array(image)
    with open(weight) as f:
        wght_arr = (np.array(json.load(f)).
                    reshape(n_size, n_size) * constant)

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
    print(
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
        print(f"RMSE : {rmse}")
        print(f"MAE : {mae}")
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


def conv_step(ff0, mtx, f0):
    f1 = mtx * f0
    f2 = sy.Eq(f1, sy.MatMul(mtx, f0, evaluate=False), evaluate=False)
    f3 = sy.Eq(ff0, f2, evaluate=False)
    return f3
