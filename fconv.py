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

# parser = argparse.ArgumentParser(
#     description='Fast convolution environment tool',
#     # epilog='Text at the bottom of help'
# )

# subparsers = parser.add_subparsers(
#     title='subcommands',
#     description='valid subcommands',
#     help='sub-command help'
# )

# # create the parser for the "a" command

# # 1D sub parser
# parser_tc1d = subparsers.add_parser(
#     'init toom-cook 1d', help='Help Toom Cook 1D', description='Toom Cook 1D'
# )
# parser_tc1d.add_argument(
#     '-p', '--points', nargs='+', default=[0, -1, 1, -2, 'inf'],
#     help=("List of points to be interpolate for Toom-Cook")
# )
# parser_tc1d.add_argument(
#     '-v', '--vector-size', nargs=2, type=int,
#     help=("Size of two vectors to be convoluted. The two sizes must be in "
#           "format P=M+N-1 where P is number of points to be interpolated "
#           "and the output size, "
#           "M and N are respectively the first and second values of the "
#           "argument. M as the size o features and N size of weights.")
# )

# parser_tc2d = subparsers.add_parser(
#     '2d', help='Help Toom Cook 2D', description='Toom Cook 2D'
# )
# parser_tc2d.add_argument(
#     '-pm', '--points-m', nargs='+', default=[0, -1, 1, -2, 'inf'],
#     help=("List of points to be interpolate for Toom-Cook")
# )
# parser_tc2d.add_argument(
#     '-pn', '--points-n', nargs='+', default=[0, -1, 1, -2, 'inf'],
#     help=("List of points to be interpolate for Toom-Cook")
# )

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


@init.group()
@click.pass_context
def toom_cook(ctx):
    pass


def count_points(ctx, param, value):
    # You can generate completions with help strings by returning a list
    # of CompletionItem. You can match on whatever you want, including
    # the help.
    #breakpoint()
    m = int(ctx.params["vector_size"][0])
    n = int(ctx.params["vector_size"][1])
    param.nargs = m + n - 1
    return value


@toom_cook.command(name="1d")
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
def one_d(points, vector_size):
    list_points = [np.inf if p == 'inf' else int(p) for p in points.split()]

    if vector_size is None:
        m_size = len(list_points) - 3 + 1
        n_size = 3
    else:
        m_size = vector_size[0]
        n_size = vector_size[1]

    c, q0, b, a = fast.toom_cook(m_size, n_size, list_points)
    q = [[int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1] for i in q0]
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
    sy.preview((c, q, b, a), viewer='file', filename='matrix.png', euler=False)



# fast_conv = [
#     fast.toom_cook_conv_1d(
#         m_size, n_size, points, weight[i], type_int=type_int
#     )
#     for i in range(n_size)
# ]
# type_int = True if args.type == "int" else False

# image = Image.open(args.file).convert('L')

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


# output = signal.convolve2d(feature, weight[::-1, ::-1], mode='valid')
# output_naive = naive_convolve(feature, weight)

# print(f"Output default and naive are equals: {np.all(output == output_naive)}")


# output_fast = np.sum(axis=0, a=[
#     fast.filter1d_slide2d(
#         fast_conv[i], feature, output.shape, i, len(points), m_size
#     )
#     for i in range(0, weight.shape[0])
# ])

# if args.type == "int":
#     mse = np.mean(np.power(output - output_fast, 2))
#     # mse = np.power(output - output_fast, 2)
#     print(f"MSE : {mse}")
# else:
#     print(
#         f"Output default and fast are equals: {np.all(output == output_fast)}"
#     )

# size = output.size

# print("Naive totals:")
# print(f"Iterations: {size}")
# print(f"Multiplications: {size * 9}")
# print(f"Additions: {size * 8}")


# print("Fast totals:")

# fast_count = fast.filter1d_slide2d_count(output.shape, m_size)
# mult = fast_count * len(points) * len(fast_conv)
# print(f"Iterations: {fast_count}")
# print(f"Multiplications: {mult}")

# add0 = fast_count * 20 * len(fast_conv)
# add1 = fast_count * 2 * len(fast_conv)
# print(f"Additions: {add0 + add1}")

# print(f"* Additions for each batch processed: {add0}")
# print(f"* Additions to join batches: {add1}")
# print(
#     f"Extra operations - bit shifts and etc: {fast_count * 9 * len(fast_conv)}"
# )

if __name__ == '__main__':
    main()
