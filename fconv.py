#!/usr/bin/env python

import json
from pathlib import Path

import click
import numpy as np
import sympy as sy
from PIL import Image
from scipy import signal
from sklearn import metrics
# from matplotlib import pyplot as plt

from lib.naive import naive_convolve
from lib import fast

root = Path(__file__).resolve().parent


def unpack_init(init_data):
    d = init_data["d"]
    m = init_data["m"]
    n = init_data["n"]
    return d, m, n


def unpack_build(build_data):
    p = build_data["p"]
    c = sy.Matrix(build_data["c"])
    b = sy.Matrix(build_data["b"])
    a = sy.Matrix(build_data["a"])
    q = sy.Matrix([
        sy.Rational(p, q) for p, q in build_data["q"]
    ])
    return p, c, b, a, q


def read_p1d():
    file = Path('init.json')
    if file.exists() is False:
        return 1
    with open(file) as f:
        init_file = json.load(f)
    init_data = unpack_init(init_file)
    d, m, n = init_data
    p = m + n - 1
    return p


def func_toom_cook(points, dimension):
    with open('init.json') as f:
        init_file = json.load(f)
    init_data = unpack_init(init_file)
    d_size, m_size, n_size = init_data
    i_size = m_size + n_size - 1
    list_points = [np.inf if p == 'inf' else int(p) for p in points]

    c, q, b, a = fast.toom_cook(m_size, n_size, list_points)
    fi = sy.Matrix(sy.symbols(" ".join(f"f_{i}"for i in range(i_size))))
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
    with open(f'build{dimension}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # TODO export matrix form too
    mul = sy.MatMul(a.T, bg, c.T, fi)
    sy.preview(
        mul, viewer='file',
        filename=f'build_filt{dimension}.png', euler=False
    )


@click.group()
@click.pass_context
def main(ctx): pass


@main.command(
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format C=B+A-1 or A=-B+C+1 where P is number of points to be interpolated "
          "and the output size, "
          "M and N are respectively the first and second values of the "
          "argument. M as the size o features and N size of weights.")
)
@click.option(
    "--dimensions", "--dim", "-d",
    required=True,
    type=click.Choice(['1', '2'])
)
@click.option('-m', required=True, type=int)
@click.option('-n', default=3)
def init(dimensions, m, n):
    file = Path("init.json")
    if file.exists():
        click.echo(
            message="init.json existis, fconv model already initialized"
        )
        click.Abort()
        exit(1)

    data = {
        "d": dimensions,
        "m": int(m),
        "n": int(n),
    }
    with open('init.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    click.echo("Initialized")


@main.group()
def build(): pass


@build.group(name="1d")
def d1(): pass


@d1.command()
@click.option(
    '--points', '-p', default=["0", "-1", "1", "-2", 'inf'], nargs=read_p1d(),
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook.")
)
def toom_cook1d(points):
    # TODO break if user was trying to use for 2D
    func_toom_cook(points, '1')
    click.echo("Builded 1D Toom Cook")


@build.group(name="2d")
@click.option(
    "--design", "-d", type=click.Choice(['iterated', 'nested']),
    default='iterated',
)
def d2(design): pass


@d2.command(name="toom-cook")
@click.option(
    '--points', '-p', default=["0", "-1", "1", "-2", 'inf'], nargs=read_p1d(),
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook.")
)
@click.option('--dimension', '--dim', '-d', type=click.Choice(['1', '2']),)
def toom_cook2d(points, dimension):
    func_toom_cook(points, dimension)
    click.echo(f"Builded 2D Toom Cook dimension {dimension}.")


@main.group()
@click.option(
    "--constant", "--const", "-c", type=int, default=1,
    help=("Constant to multiply the weight.")
)
@click.option("--integer", "--int", "-i", flag_value=True)
@click.option("--fixed-point", "-x", flag_value=True)
@click.option("--float-point", "-l", flag_value=True)
@click.pass_context
def quant(ctx): pass


@main.group()
@click.pass_context
def sim(ctx): pass


@sim.command()
@click.option(
    "--feature", "-f", default=root / "images" / "karatsuba032.jpg",
    help=("Feature file, can be a image or json list file.")
)
@click.option(
    "--weight", "-w", default=root / "images" / "laplace.json",
    help=("Weight file, need to be a json list file.")
)
def define(feature, weight):
    with open('init.json') as f:
        init_file = json.load(f)
    init = unpack_init(init_file)
    m_size, n_size, points, c, b, a, q = init

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
        print(
            f"Output default and fast are equals: {compare_fast}"
        )

    size = output_default.size

    print("Naive totals:")
    print(f"Iterations: {size}")
    print(f"Multiplications: {size * 9}")
    print(f"Additions: {size * 8}")

    print("Fast totals:")
    fast_count = fast.filter1d_slide2d_count(output_default.shape, m_size)
    mult = fast_count * len(points) * len(fast_conv)
    print(f"Iterations: {fast_count}")
    print(f"Multiplications: {mult}")
    add0 = fast_count * 20 * len(fast_conv)
    add1 = fast_count * 2 * len(fast_conv)
    print(f"Additions: {add0 + add1}")
    print(f"* Additions for each batch processed: {add0}")
    print(f"* Additions to join batches: {add1}")
    print(
        f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
    )


@sim.command()
# @click.option(
#     "--constant", "--const", "-c", type=int, default=1,
#     help=("Constant to multiply the weight.")
# )
@click.option(
    "--image-side", "-s", default=32,
    help=("Image side, must be a power of two.")
)
@click.option(
    "--loop", "-L", default=1,
    help=("Total of execution loops.")
)
@click.option(
    "--feature-random", "-f", nargs=2, default=[0, 256],
    help=("Minimal and maximal value of feature random data.")
)
@click.option(
    "--weight-random", "-w", nargs=2, default=[0, 1024],
    help=("Minimal and maximal value of weight random data.")
)
@click.option("--integer", "--int", "-i", flag_value=True)
def random(feature_random, weight_random, image_side, integer, loop):
    with open('init.json') as f:
        init_file = json.load(f)
    init = unpack_init(init_file)
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
        print(
            f"Output default and fast are equals: {compare_fast}"
        )

    size = output_default.size

    print("Naive totals:")
    print(f"Iterations: {size}")
    print(f"Multiplications: {size * 9}")
    print(f"Additions: {size * 8}")

    print("Fast totals:")

    fast_count = fast.filter1d_slide2d_count(output_default.shape, m_size)
    mult = fast_count * len(points) * len(fast_conv)
    print(f"Iterations: {fast_count}")
    print(f"Multiplications: {mult}")

    add0 = fast_count * 20 * len(fast_conv)
    add1 = fast_count * 2 * len(fast_conv)

    print(f"Additions: {add0 + add1}")
    print(f"* Additions for each batch processed: {add0}")
    print(f"* Additions to join batches: {add1}")
    print(
        f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
    )


if __name__ == '__main__':
    main()
