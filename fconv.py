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


@click.group()
@click.pass_context
def main(ctx): pass


@main.group()
@click.pass_context
def init(ctx): pass


@main.group()
@click.pass_context
def sim(ctx): pass


@init.group(name="1d")
@click.pass_context
def one_d(ctx): pass


@init.group(name="2d")
@click.option(
    "--design", "-d", type=click.Choice(['iterated', 'nested']),
    default='iterated',
)
@click.pass_context
def two_d(ctx, design):
    ctx.ensure_object(dict)
    ctx.obj["design"] = design


def count_points(ctx, param, value):
    # You can generate completions with help strings by returning a list
    # of CompletionItem. You can match on whatever you want, including
    # the help.
    m = int(ctx.params["vector_size"][0])
    n = int(ctx.params["vector_size"][1])
    param.nargs = m + n - 1
    return value


@one_d.command()
@click.option(
    '--vector_size', '-v', required=False, nargs=2,
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format P=M+N-1 where P is number of points to be interpolated "
          "and the output size, "
          "M and N are respectively the first and second values of the "
          "argument. M as the size o features and N size of weights.")
)
@click.option(
    '--points', '-p', default="0 -1 1 -2 inf",
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook. "
          "Must use quotation marks: '0 -1 1 -2 inf'.")
)
def toom_cook(points, vector_size):
    list_points = [np.inf if p == 'inf' else int(p) for p in points.split()]

    if vector_size is None:
        m_size = len(list_points) - 3 + 1
        n_size = 3
    else:
        m_size = vector_size[0]
        n_size = vector_size[1]

    c, q0, b, a = fast.toom_cook(m_size, n_size, list_points)
    q = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q0
    ]
    data = {
        "points": list_points,
        "m": m_size,
        "n": n_size,
        "c": np.array(c, dtype=int).tolist(),
        "q": q,
        "b": np.array(b, dtype=int).tolist(),
        "a": np.array(a, dtype=int).tolist(),
    }
    with open('init.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    sy.preview(
        (c, q, b, a), viewer='file', filename='conv_matrix.png', euler=False
    )
    sy.preview(
        (a.T, q, b, c.T), viewer='file', filename='filt_matrix.png',
        euler=False
    )


@two_d.command(name="toom-cook")
@click.option(
    '--vector_size0', '-v1', required=False, nargs=2,
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format P=M+N-1 where P is number of points to be interpolated "
          "and the output size, "
          "M and N are respectively the first and second values of the "
          "argument. M as the size o features and N size of weights.")
)
@click.option(
    '--vector_size1', '-v2', required=False, nargs=2,
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format P=M+N-1 where P is number of points to be interpolated "
          "and the output size, "
          "M and N are respectively the first and second values of the "
          "argument. M as the size o features and N size of weights.")
)
@click.option(
    '--points0', '-p1', default="0 -1 1 -2 inf",
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook. "
          "Must use quotation marks: '0 -1 1 -2 inf'.")
)
@click.option(
    '--points1', '-p2', default="0 -1 1 -2 inf",
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook. "
          "Must use quotation marks: '0 -1 1 -2 inf'.")
)
def toom_cook2d(points0, points1, vector_size0, vector_size1):
    list_points0 = [np.inf if p == 'inf' else int(p) for p in points0.split()]
    list_points1 = [np.inf if p == 'inf' else int(p) for p in points1.split()]

    if vector_size0 is None:
        m_size0 = len(list_points0) - 3 + 1
        n_size0 = 3
    else:
        m_size0 = vector_size0[0]
        n_size0 = vector_size0[1]

    if vector_size1 is None:
        m_size1 = len(list_points1) - 3 + 1
        n_size1 = 3
    else:
        m_size1 = vector_size1[0]
        n_size1 = vector_size1[1]

    c0, _q0, b0, a0 = fast.toom_cook(m_size0, n_size0, list_points0)
    q0 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in _q0
    ]
    c1, _q1, b1, a1 = fast.toom_cook(m_size1, n_size1, list_points1)
    q1 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in _q1
    ]

    data = {
        "1d": {
            0: {
                "points": list_points0,
                "m": m_size0,
                "n": n_size0,
                "c": np.array(c0, dtype=int).tolist(),
                "q": q0,
                "b": np.array(b0, dtype=int).tolist(),
                "a": np.array(a0, dtype=int).tolist(),
            },
            1: {
                "points": list_points1,
                "m": m_size1,
                "n": n_size1,
                "c": np.array(c1, dtype=int).tolist(),
                "q": q1,
                "b": np.array(b1, dtype=int).tolist(),
                "a": np.array(a1, dtype=int).tolist(),
            }
        }
    }
    with open('init.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    sy.preview(
        (c0, q0, b0, a0), viewer='file', filename='conv_matrix0.png',
        euler=False
    )
    sy.preview(
        (a0.T, q0, b0, c0.T), viewer='file', filename='filt_matrix0.png',
        euler=False
    )
    sy.preview(
        (c1, q1, b1, a1), viewer='file', filename='conv_matrix1.png',
        euler=False
    )
    sy.preview(
        (a1.T, q1, b1, c1.T), viewer='file', filename='filt_matrix1.png',
        euler=False
    )


@main.group()
@click.pass_context
def sim(ctx): pass


@sim.command()
@click.option(
    "--constant", "--const", "-c", type=int, default=1,
    help=("Constant to multiply the weight.")
)
@click.option(
    "--feature", "-f", default=root / "images" / "karatsuba032.jpg",
    help=("Feature file, can be a image or json list file.")
)
@click.option(
    "--weight", "-w", default=root / "images" / "laplace.json",
    help=("Weight file, need to be a json list file.")
)
@click.option("--integer", "--int", "-i", flag_value=True)
def define(feature, weight, constant, integer):
    with open('init.json') as f:
        init_file = json.load(f)
    init = unpack_init(init_file)
    m_size, n_size, points, c, b, a, q = init

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


def unpack_init(init):
    m = init["m"]
    n = init["n"]
    p = init["points"]
    c = sy.Matrix(init["c"])
    b = sy.Matrix(init["b"])
    a = sy.Matrix(init["a"])
    q = sy.Matrix([
        sy.Rational(p, q) for p, q in init["q"]
    ])
    return m, n, p, c, b, a, q


if __name__ == '__main__':
    main()
