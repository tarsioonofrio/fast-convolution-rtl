#!/usr/bin/env python

import os
from pathlib import Path

import click

from .commands import (
    cmd_init, cmd_build_toom_cook, cmd_sim_file, cmd_sim_random,
    read_num_points, conv_step,
)


root = Path(os.getcwd())


@click.group()
@click.pass_context
def main(ctx): pass


@main.group(
    help=("Size of two vectors to be convoluted. The two sizes must be in "
          "format C=B+A-1 or A=-B+C+1 where P is number of points to be interpolated "
          "and the output size, "
          "M and N are respectively the first and second values of the "
          "argument. M as the size o features and N size of weights.")
)
def init(): pass


@init.command(name="1d")
@click.option('-m', required=True, type=int)
@click.option('-n', default=3)
def init1d(m, n):
    cmd_init(1, m, n)

@init.command(name="2d")
@click.option('-m', required=True, nargs=2)
@click.option('-n', default=[3, 3], nargs=2)
def init1d(m, n):
    cmd_init(2, m, n)


@main.group()
def build(): pass


@build.group(name="1d")
def build_d1(): pass


@build_d1.command(name="toom-cook")
@click.option(
    '--points', '-p', default=["0", "-1", "1", "-2", 'inf'],
    nargs=read_num_points(), show_default=True,
    help=("List of points to be interpolate for Toom-Cook.")
)
def toom_cook1d(points):
    # TODO break if user was trying to use for 2D
    cmd_build_toom_cook(points)
    click.echo("Builded 1D Toom Cook")


@build_d1.command()
@click.option(
    '--s', '-s', default=[5, 5], show_default=True,
    help=("Not implemented.")
)
def cyclic_to_linear(points): pass


@build.group(name="2d")
def build_d2(design): pass


@build_d2.command(name="toom-cook")
@click.option(
    '--points', '-p', default=["0", "-1", "1", "-2", 'inf'],
    nargs=read_num_points(), show_default=True,
    help=("List of points to be interpolate for Toom-Cook.")
)
@click.option('--dimension', '--dim', '-d', type=click.Choice(['1', '2']),)
def toom_cook2d(points, dimension):
    cmd_build_toom_cook(points, dimension)
    click.echo(f"Builded 2D Toom Cook dimension {dimension}.")

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


@main.group()
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
    "--feature", "-f", default=root / "images" / "karatsuba032.jpg",
    help=("Feature file, can be a image or json list file.")
)
@click.option(
    "--weight", "-w", default=root / "images" / "laplace.json",
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
