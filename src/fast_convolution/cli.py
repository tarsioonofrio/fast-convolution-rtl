#!/usr/bin/env python

import os
from pathlib import Path

import click

from .commands import (
    read_init_if_exists,
    num_points1d, num_points2d,
    default_toom_cook_points1d, default_toom_cook_points2d,
)


def example_path():
    return Path(__file__).resolve().parent.parent.parent / "images"


def ctx_fn():
    return click.get_current_context().info_name


class Repo(object):
    def __init__(self, path=None, debug=False):
        self.root = Path(os.path.abspath(path or '.'))
        self.debug = debug
        self.dir_config = self.root / "config"
        self.file_init = self.dir_config / "init.json"
        self.file_build = self.dir_config / "build.json"
        self.file_bind = self.dir_config / "bind.json"
        self.file_quant = self.dir_config / "quant.json"
        self.dir_build = self.root / "build"
        self.dir_quant = self.root / "quant"
        self.dir_example = self.root / "example"
        self.dir_sim = self.root / "sim"
        self.dir_clib = self.root / "clib"
        self.dir_clib_data = self.dir_clib / "data"


@click.group()
@click.option('-p', '--path', envvar='PATH_REPO', default='.')
@click.pass_context
def main(ctx, path):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj = Repo(path)
    # init_data = read_init_if_exists()
    # ctx.obj['init'] = init_data
    # example_path = Path(__file__).resolve().parent.parent.parent / "images"
    # ctx.obj['example_path'] = example_path


@main.group(
    short_help="Initialize fast convolution repo.",
    help="Size of two vectors to be convoluted. The two sizes must be in "
          "format Out = In - W + 1 or In = Out + W - 1 where In is the number of"
          "elements in the input, Out is the number of elements in the the "
          "the output, and W is the number of elements of weights or kernel."
)
def init(): pass


@init.command(name="1d")
@click.option('-i', '--in-len', default=None, type=int)
@click.option('-o', '--out-len', default=None, type=int)
@click.option('-w', default=3, type=int)
@click.pass_obj
def init1d(repo, in_len, out_len, w):
    from .commands import cmd_init
    msg = cmd_init(repo, 1, in_len, out_len, w)
    if msg is not None:
        click.echo(msg)


@init.command(name="2d")
@click.option('-i', '--in-len', nargs=2, default=None, type=int)
@click.option('-o', '--out-len', nargs=2, default=None, type=int)
@click.option('-w', default=[3, 3], nargs=2)
@click.pass_obj
def init2d(repo, in_len, out_len, w):
    from .commands import cmd_init
    cmd_init(repo, 2, in_len, out_len, w)


# @main.command(help="Show config files")
# @click.option('-i', '--init', name="init_", flag_value=True)
# @click.option('-b', '--build', name="build_", flag_value=True)
# @click.option('-q', '--quant', name="quant_", flag_value=True)
# @click.pass_obj
# def show(repo, init_, build_, quant_):
#     from .commands import cmd_show
#     msg = cmd_show(repo, init_, build_, quant_)
#     if msg is not None:
#         click.echo(msg)


@main.group(help="Build fast convolution")
def build(): pass


# @build.group(name="1d", hidden=init_data.get("dim", 1) == 2)
@build.group(name="1d")
def build_d1(): pass


@build_d1.command(name="toom-cook")
@click.option(
    '--points', '-p', type=str,
    # default=default_toom_cook_points1d(read_init_if_exists(repo).get("c", 1)), show_default=True,
    # nargs=num_points1d(read_init_if_exists(repo).get("c", 1)),
    help="List of points to be interpolate for Toom-Cook."
)
@click.pass_obj
def toom_cook1d(repo, points):
    # TODO break if user was trying to use for 2D
    from .commands import cmd_build_toom_cook1d
    nargs = num_points1d(read_init_if_exists(repo).get("c", 1))
    if points is not None:
        if len(points) != nargs:
            click.Abort()
    default = default_toom_cook_points1d(read_init_if_exists(repo).get("c", 1))
    points_ = points if points is not None else default
    cmd_build_toom_cook1d(repo, points_)
    click.echo("Build 1D Toom Cook")


@build_d1.command()
@click.option(
    '--s', '-s', default=[5, 5], show_default=True,
    help="Not implemented."
)
def cyclic_to_linear(points): pass


# @build.group(name="2d", hidden=init_data.get("dim", 2) == 1)
@build.group(name="2d")
def build_d2(): pass


@build_d2.command(name="toom-cook")
@click.option(
    '--points-1d', '--p1', type=str,
    # default=default_toom_cook_points2d(read_init_if_exists(repo).get("c", 1), 0), show_default=True,
    # nargs=num_points2d(read_init_if_exists(repo).get("c", 1), 0),
    help="List of points to be interpolate for Toom-Cook first dimension."
)
@click.option(
    '--points-2d', '--p2', type=str,
    # default=default_toom_cook_points2d(read_init_if_exists(repo).get("c", 1), 1), show_default=True,
    # nargs=num_points2d(read_init_if_exists(repo).get("c", 1), 1),
    help="List of points to be interpolate for Toom-Cook second dimension."
)
@click.pass_obj
def toom_cook2d(repo, points_1d, points_2d):
    from .commands import cmd_build_toom_cook2d
    nargs1 = num_points2d(read_init_if_exists(repo).get("c", 1), 0)
    nargs2 = num_points2d(read_init_if_exists(repo).get("c", 1), 1)
    if points_1d is not None:
        if len(points_1d) != nargs1:
            click.Abort()
    if points_2d is not None:
        if len(points_2d) != nargs2:
            click.Abort()
    default1 = default_toom_cook_points2d(read_init_if_exists(repo).get("c", 1), 0)
    default2 = default_toom_cook_points2d(read_init_if_exists(repo).get("c", 1), 1)
    points_1d_ = points_1d if points_1d is not None else default1
    points_2d_ = points_2d if points_2d is not None else default2
    cmd_build_toom_cook2d(repo, points_1d_, points_2d_)
    click.echo("Build 2D Toom Cook dimension.")


# @build_d2.command()
# @click.option(
#     '--s', '-s', default=[5, 5], nargs=2, show_default=True,
#     help="Not implemented.")
# )
# def cyclic_to_linear(points): pass


@build_d2.group(help="Bind multiple dimensions")
def bind(): pass


@bind.command(name="iter", help="Iterated multidimensional bind")
@click.pass_obj
def iterate(ctx):
    from .commands import cmd_build2d_bind_iterate
    cmd_build2d_bind_iterate(ctx)


@bind.command(help="Nested multidimensional bind")
@click.pass_obj
def nest(ctx):
    from .commands import cmd_build2d_bind_nest
    cmd_build2d_bind_nest(ctx)


@main.group(help="Quantization")
# @click.option(
#     "--constant", "--const", "-c", type=int, default=1,
#     help="Constant to multiply the weight.")
# )
# @click.option("--integer", "--int", "-i", flag_value=True)
# @click.option("--fixed-point", "-x", flag_value=True)
# @click.option("--float-point", "-l", flag_value=True)
# @click.pass_obj
def quant(): pass


@quant.command(help="Set quantization to none", name="none")
@click.pass_obj
def no_quant(repo):
    from .commands import cmd_quant_none
    cmd_quant_none(repo)


@quant.command(help="Shift quantization")
@click.option(
    "--bits", "-b", default=2, show_default=True,
    help="Number of bits to be shifted."
)
@click.pass_obj
def shift(repo, bits):
    from .commands import cmd_quant_shift
    cmd_quant_shift(repo, bits)
    click.echo("Shift quantization")


@main.group(help="Simulation")
def sim(): pass


@sim.command(help="Simulation using file")
@click.option(
    "--feature", "-f", default=example_path() / "karatsuba032.jpg",
    help="Feature file, can be a image or json list file."
)
@click.option(
    "--weight", "-w", default=example_path() / "laplace.json",
    help="Weight file, need to be a json list file."
)
@click.pass_obj
# @click.option("--mae", flag_value=True, help="Mean absolute error")
# @click.option("--mse", flag_value=True, help="Mean squared error")
# @click.option("--rmse", flag_value=True, help="Root mean squared error")
# @click.option("--r2", flag_value=True, help="R2", default=True)
def file(repo, feature, weight):
    from .commands import cmd_sim_file
    text = cmd_sim_file(repo, feature, weight)
    click.echo(text)


@sim.command(help="Simulation with random numbers")
# @click.option(
#     "--constant", "--const", "-c", type=int, default=1,
#     help="Constant to multiply the weight.")
# )
@click.option(
    "--image-side", "-s", default=32,
    help="Image side, must be a power of two."
)
@click.option(
    "--loop", "-L", default=1,
    help="Total of execution loops. Not implemented"
)
@click.option(
    "--feature", "-f", nargs=2, default=[0, 256],
    help="Minimal and maximal value of feature random data."
)
@click.option(
    "--weight", "-w", nargs=2, default=[0, 1024],
    help="Minimal and maximal value of weight random data."
)
@click.pass_obj
def rand(repo, feature, weight, image_side, loop):
    from .commands import cmd_sim_random
    text = cmd_sim_random(repo, feature, weight, image_side, loop)
    click.echo(text)


@main.group(help="Create example")
def example(): pass


@example.command(help="Example with random numbers")
@click.option(
    "--feature", "-f", nargs=2, default=[0, 256],
    help="Minimal and maximal value of feature random data."
)
@click.option(
    "--weight", "-w", nargs=2, default=[0, 1024],
    help="Minimal and maximal value of weight random data."
)
@click.pass_obj
def rand(repo, feature, weight):
    from .commands import cmd_example_random
    cmd_example_random(repo, feature, weight)
    click.echo("Random example")


@example.command(help="Example with sequential numbers")
@click.option(
    "--feature", "-f", default=0,
    help="Minimal value of sequential feature data."
)
@click.option(
    "--weight", "-w", default=0,
    help="Minimal value of sequential weight data."
)
@click.pass_obj
def seq(repo, feature, weight):
    from .commands import cmd_example_sequential
    cmd_example_sequential(repo, feature, weight)
    click.echo("Sequential example")


if __name__ == '__main__':
    main()
