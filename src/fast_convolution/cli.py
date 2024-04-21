#!/usr/bin/env python

import os
from pathlib import Path

import click

from .commands import (
    cmd_init, cmd_build_toom_cook1d, cmd_build_toom_cook2d,
    cmd_sim_file, cmd_sim_random,
    read_init_if_exists, num_points1d, num_points2d,
    default_toom_cook_points1d, default_toom_cook_points2d
)


root = Path(os.getcwd())
example_path = Path(__file__).resolve().parent.parent.parent / "images"

init_data = read_init_if_exists()


@click.group()
@click.pass_context
def main(ctx): pass


@main.group(
    short_help="Initialize fast convolution repo with the sizes of vectors.",
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format Out = In - W + 1 or In = Out + W - 1 where In is the number of"
          "elements in the input, Out is the number of elements in the the "
          "the output, and W is the number of elements of weights or kernel.")
)
def init(): pass


@init.command(name="1d")
@click.option('-i', '--in-len', default=None, type=int)
@click.option('-o', '--out-len', default=None, type=int)
@click.option('-w', default=3, type=int)
def init1d(in_len, out_len, w):
    cmd_init(1, in_len, out_len, w)


@init.command(name="2d")
@click.option('-i', '--in-len', nargs=2, default=None, type=int)
@click.option('-o', '--out-len', nargs=2, default=None, type=int)
@click.option('-w', default=[3, 3], nargs=2)
def init2d(in_len, out_len, w):
    cmd_init(2, in_len, out_len, w)


@main.group()
def build(): pass


@build.group(name="1d", hidden=init_data["dim"] == 2)
def build_d1(): pass


@build_d1.command(name="toom-cook")
@click.option(
    '--points', '-p',
    default=default_toom_cook_points1d(init_data["c"]),
    nargs=num_points1d(init_data["c"]), show_default=True,
    help=("List of points to be interpolate for Toom-Cook.")
)
def toom_cook1d(points):
    # TODO break if user was trying to use for 2D
    cmd_build_toom_cook1d(points)
    click.echo("Builded 1D Toom Cook")


@build_d1.command()
@click.option(
    '--s', '-s', default=[5, 5], show_default=True,
    help=("Not implemented.")
)
def cyclic_to_linear(points): pass


@build.group(name="2d", hidden=init_data["dim"] == 1)
def build_d2(): pass


@build_d2.command(name="toom-cook")
@click.option(
    '--points1d', '-1',
    default=default_toom_cook_points2d(init_data["c"], 0),
    nargs=num_points2d(init_data["c"], 0),
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook first dimension.")
)
@click.option(
    '--points2d', '-2',
    default=default_toom_cook_points2d(init_data["c"], 1),
    nargs=num_points2d(init_data["c"], 1),
    show_default=True,
    help=("List of points to be interpolate for Toom-Cook second dimension.")
)
def toom_cook2d(points1d, points2d):
    cmd_build_toom_cook2d(points1d, points2d)
    click.echo("Builded 2D Toom Cook dimension.")


@build_d2.command()
@click.option(
    '--s', '-s', default=[5, 5], nargs=2, show_default=True,
    help=("Not implemented.")
)
def cyclic_to_linear(points): pass


@build_d2.command()
@click.option(
    "--design", "-d", type=click.Choice(['iterated', 'nested']),
    default='iterated', help=("Not implemented.")
)
def bind(design): pass


@main.group(help="Not implemented yet")
# @click.option(
#     "--constant", "--const", "-c", type=int, default=1,
#     help=("Constant to multiply the weight.")
# )
# @click.option("--integer", "--int", "-i", flag_value=True)
# @click.option("--fixed-point", "-x", flag_value=True)
# @click.option("--float-point", "-l", flag_value=True)
# @click.pass_context
def quant(ctx): pass


@main.group()
@click.pass_context
def sim(ctx): pass


@sim.command()
@click.option(
    "--feature", "-f", default=example_path / "karatsuba032.jpg",
    help=("Feature file, can be a image or json list file.")
)
@click.option(
    "--weight", "-w", default=example_path / "laplace.json",
    help=("Weight file, need to be a json list file.")
)
def file(feature, weight):
    cmd_sim_file(feature, weight)


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
    cmd_sim_random(feature_random, weight_random, image_side, integer, loop)


if __name__ == '__main__':
    main()
