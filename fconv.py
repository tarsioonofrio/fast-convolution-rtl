#!/usr/bin/env python

import json
from pathlib import Path

import click
import numpy as np
import sympy as sy
from PIL import Image
from scipy import signal
# from matplotlib import pyplot as plt

from lib.naive import naive_convolve
from lib import fast 

root = Path(__file__).resolve().parent
# # SIM sub parser
# parser_sim = subparsers.add_parser(
#     'sim', help='Help simulation', description="Sim"
# )

# parser_sim.add_argument(
#     '-t', '--type', default="float", choices=("int", "float"), help="Data type"
# )
# parser_sim.add_argument(
#     '-c', '--const', default=1, type=int,
#     help="Constant value to multiply all data"
# )
# parser_sim.add_argument('-f', '--file', type=Path)
# parser_sim.add_argument(
#     '-I', '--interactions', type=int,  help="Image side of random data"
# )
# parser_sim.add_argument(
#     '-r', '--random', type=int,  nargs=2,
#     help="Lowest and highest value of random data"
# )
# parser_sim.add_argument(
#     '-i', '--image-side', type=int, default=32,
#     help="Image side of random data"
# )

# args = parser.parse_args()

# @click.option('--repo-home', envvar='REPO_HOME', default='.repo')
# @click.option('--debug/--no-debug', default=False,
#               envvar='REPO_DEBUG')

@click.group()
@click.pass_context
def main(ctx):
    pass
    # ctx.obj = Repo(repo_home, debug)

@main.group()
@click.pass_context
def init(ctx):
    pass
    # ctx.obj = Repo(repo_home, debug)


@main.group()
@click.pass_context
def sim(ctx):
    pass


@init.group(name="1d")
@click.pass_context
def one_d(ctx):
    pass


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
        "matrix": {
            "c": np.array(c, dtype=int).tolist(),
            "q": q,
            "b": np.array(b, dtype=int).tolist(),
            "a": np.array(a, dtype=int).tolist(),
        }
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


@main.group()
@click.pass_context
def sim(ctx):
    pass
    # ctx.obj = Repo(repo_home, debug)

@sim.command()
@click.option(
    "--feature", "-f", default=root / "images" / "karatsuba032.jpg",
    help=("Feature file, can be a image or json list file.")
)
@click.option(
    "--weight", "-w", default=root / "images" / "laplace.json",
    help=("Weight file, need to be a json list file.")
)
@click.option("--integer", "--int", "-i", flag_value=True)
def define(feature, weight, integer):
    with open('init.json') as f:
        init = json.load(f)
    m_size = init["m"]
    n_size = init["n"]
    points = init["points"]
    matrix = init["matrix"]
    c = sy.Matrix(matrix["c"])
    b = sy.Matrix(matrix["b"])
    a = sy.Matrix(matrix["a"])
    q = sy.Matrix([
        sy.Rational(p, q) for p, q in matrix["q"]
    ])

    with open(feature) as f:
        image = Image.open(feature).convert('L')
        feat_arr = np.array(image)
    with open(weight) as f:
        wght_arr = np.array(json.load(f)).reshape(n_size, n_size)

    type_int = True if integer == "int" else False
    fast_conv = [
        fast.conv1d(
            wght_arr[i], c, q, b, a, type_int=type_int
        )
        for i in range(n_size)
    ]

    output = signal.convolve2d(feat_arr, wght_arr[::-1, ::-1], mode='valid')
    output_naive = naive_convolve(feat_arr, wght_arr)

    print(
        f"Output default and naive are equals: {np.all(output == output_naive)}"
    )

    output_fast = np.sum(axis=0, a=[
        fast.filter1d_slide2d(
            fast_conv[i], feat_arr, output.shape, i, len(points), m_size
        )
        for i in range(0, wght_arr.shape[0])
     ])

    if integer:
        mse = np.mean(np.power(output - output_fast, 2))
        # mse = np.power(output - output_fast, 2)
        print(f"MSE : {mse}")
    else:
        compare = np.all(output == output_fast)
        print(
            f"Output default and fast are equals: {compare}"
        )

    size = output.size

    print("Naive totals:")
    print(f"Iterations: {size}")
    print(f"Multiplications: {size * 9}")
    print(f"Additions: {size * 8}")

    print("Fast totals:")

    fast_count = fast.filter1d_slide2d_count(output.shape, m_size)
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



# if args.random is None:
#     feature = np.array(image)
# else:
#     feature0 = np.random.randint(
#         args.random[0], args.random[1], size=args.image_side ** 2
#     )
#     feature = feature0.reshape(args.image_side, args.image_side)


# if args.random is None:
#     weight = np.array([
#         [0, 1, 0],
#         [1, -4, 1],
#         [0, 1, 0],
#     ])
# else:
#     weight0 = np.random.randint(
#         args.random[0], args.random[1], size=n_size ** 2
#     )
#     weight = weight0.reshape(n_size, n_size)



if __name__ == '__main__':
    main()
