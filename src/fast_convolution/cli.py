#!/usr/bin/env python

import os
import sys
import traceback
from pathlib import Path

import click
import ipdb as pdb

from .commands import (
    default_toom_cook_points1d,
    default_toom_cook_points2d,
    num_points1d,
    num_points2d,
    read_init_if_exists,
)


def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    pdb.post_mortem(tb)

sys.excepthook = excepthook


def example_path():
    return Path(__file__).resolve().parent.parent.parent / "images"


def ctx_fn():
    return click.get_current_context().info_name


class Repo(object):
    def __init__(self, path=None, debug=False):
        self.root = Path(os.path.abspath(path or "."))
        self.debug = debug
        self.dir_config = self.root / "config"
        self.file_init = self.dir_config / "init.json"
        self.file_build = self.dir_config / "build.json"
        self.file_gen = self.dir_config / "gen.json"
        self.file_bind = self.dir_config / "bind.json"
        self.file_quant = self.dir_config / "quant.json"
        self.dir_build = self.root / "build"
        self.dir_quant = self.root / "quant"
        self.dir_example = self.root / "example"
        self.dir_sim = self.root / "sim"
        self.dir_clib = self.root / "clib"
        self.dir_sv = self.root / "sv"
        self.dir_clib_make = self.dir_clib / "make"
        self.dir_clib_lib = self.dir_clib / "lib"
        self.dir_clib_main = self.dir_clib / "main"
        self.dir_clib_data = self.dir_clib / "data"
        self.dir_clib_data_float = self.dir_clib / "data_float"


@click.group()
@click.option("-p", "--path", envvar="PATH_REPO", default=".")
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
    "the output, and W is the number of elements of weights or kernel.",
)
def init():
    pass


@init.command(name="1d")
@click.option("-i", "--in-len", default=None, type=int)
@click.option("-o", "--out-len", default=None, type=int)
@click.option("-w", default=3, type=int)
@click.pass_context
def init1d(ctx, in_len, out_len, w):
    from .commands import cmd_init

    repo = ctx.obj
    msg = cmd_init(repo, 1, in_len, out_len, w)
    if msg is not None:
        click.echo(msg)


@init.command(name="2d")
@click.option("-i", "--in-len", default=None, type=int)
@click.option("-o", "--out-len", default=None, type=int)
@click.option("-w", default=3)
@click.pass_context
def init2d(ctx, in_len, out_len, w):
    from .commands import cmd_init

    repo = ctx.obj
    cmd_init(repo, 2, in_len, out_len, w)


# @main.command(help="Show config files")
# @click.option('-i', '--init', name="init_", flag_value=True)
# @click.option('-b', '--build', name="build_", flag_value=True)
# @click.option('-q', '--quant', name="quant_", flag_value=True)
# @click.pass_context
# def show(repo, init_, build_, quant_):
#     from .commands import cmd_show
#     msg = cmd_show(repo, init_, build_, quant_)
#     if msg is not None:
#         click.echo(msg)


@main.group(help="Build fast convolution")
def build():
    pass


# @build.group(name="1d", hidden=init_data.get("dim", 1) == 2)
@build.group(name="1d")
def build_d1():
    pass


@build_d1.command(name="toom-cook")
@click.option(
    "--points",
    "-p",
    type=str,
    # default=default_toom_cook_points1d(read_init_if_exists(repo).get("c", 1)), show_default=True,
    # nargs=num_points1d(read_init_if_exists(repo).get("c", 1)),
    help="List of points to be interpolate for Toom-Cook.",
)
@click.pass_context
def toom_cook1d(ctx, points):
    # TODO break if user was trying to use for 2D
    from .commands import cmd_build_toom_cook1d

    repo = ctx.obj
    nargs = num_points1d(read_init_if_exists(repo).get("c", 1))
    if points is not None:
        if len(points) != nargs:
            click.Abort()
    default = default_toom_cook_points1d(read_init_if_exists(repo).get("c", 1))
    points_ = points if points is not None else default

    cmd_build_toom_cook1d(repo, points_)
    click.echo("Build 1D Toom Cook")


@build_d1.command(name="manual", help="6 multiplications")
@click.pass_context
def manual1d(ctx):
    # TODO break if user was trying to use for 2D
    from .commands import cmd_build_manual_factorization1d

    repo = ctx.obj
    cmd_build_manual_factorization1d(repo)
    click.echo("Build 1D manual factorization")


@build_d1.command()
@click.option(
    "--s", "-s", default=[5, 5], show_default=True, help="Not implemented."
)
def cyclic_to_linear(points):
    pass


# @build.group(name="2d", hidden=init_data.get("dim", 2) == 1)
@build.group(name="2d")
def build_d2():
    pass


@build_d2.command(name="toom-cook")
@click.option(
    "--points-1d",
    "--p1",
    type=str,
    # default=default_toom_cook_points2d(read_init_if_exists(repo).get("c", 1), 0), show_default=True,
    # nargs=num_points2d(read_init_if_exists(repo).get("c", 1), 0),
    help="List of points to be interpolate for Toom-Cook first dimension.",
)
@click.option(
    "--points-2d",
    "--p2",
    type=str,
    # default=default_toom_cook_points2d(read_init_if_exists(repo).get("c", 1), 1), show_default=True,
    # nargs=num_points2d(read_init_if_exists(repo).get("c", 1), 1),
    help="List of points to be interpolate for Toom-Cook second dimension.",
)
@click.pass_context
def toom_cook2d(ctx, points_1d, points_2d):
    from .commands import cmd_build_toom_cook2d

    repo = ctx.obj
    nargs1 = num_points2d(read_init_if_exists(repo).get("c", 1), 0)
    nargs2 = num_points2d(read_init_if_exists(repo).get("c", 1), 1)
    if points_1d is not None:
        if len(points_1d) != nargs1:
            click.Abort()
    if points_2d is not None:
        if len(points_2d) != nargs2:
            click.Abort()
    default1 = default_toom_cook_points2d(
        read_init_if_exists(repo).get("c", 1), 0
    )
    default2 = default_toom_cook_points2d(
        read_init_if_exists(repo).get("c", 1), 1
    )
    points_1d_ = points_1d if points_1d is not None else default1
    points_2d_ = points_2d if points_2d is not None else default2
    cmd_build_toom_cook2d(repo, points_1d_, points_2d_)
    click.echo("Build 2D Toom Cook dimension.")


@build_d2.command(name="manual", help="6x6 multiplications")
@click.pass_context
def manual2d(ctx):
    # TODO break if user was trying to use for 2D
    from .commands import cmd_build_manual_factorization2d

    repo = ctx.obj
    cmd_build_manual_factorization2d(repo)
    click.echo("Build 2D manual factorization")


# @build_d2.command()
# @click.option(
#     '--s', '-s', default=[5, 5], nargs=2, show_default=True,
#     help="Not implemented.")
# )
# def cyclic_to_linear(points): pass


@build_d2.group(help="Bind multiple dimensions")
def bind():
    pass


@bind.command(name="nest", help="Nestedted multidimensional bind")
@click.pass_context
def nest(ctx):
    from .commands import cmd_build2d_bind_nest

    repo = ctx.obj
    cmd_build2d_bind_nest(repo)


@bind.command(help="Kronecker multidimensional bind")
@click.pass_context
def kron(ctx):
    from .commands import cmd_build2d_bind_kron

    repo = ctx.obj
    cmd_build2d_bind_kron(repo)


@main.group(help="Quantization")
# @click.option(
#     "--constant", "--const", "-c", type=int, default=1,
#     help="Constant to multiply the weight.")
# )
# @click.option("--integer", "--int", "-i", flag_value=True)
# @click.option("--fixed-point", "-x", flag_value=True)
# @click.option("--float-point", "-l", flag_value=True)
# @click.pass_context
def quant():
    pass


@quant.command(help="Set quantization to none", name="none")
@click.pass_context
def no_quant(ctx):
    from .commands import cmd_quant_none

    repo = ctx.obj
    cmd_quant_none(repo)


@quant.command(help="Shift quantization")
@click.option(
    "--bits",
    "-b",
    default=4,
    show_default=True,
    help="Number of bits to be shifted.",
)
@click.pass_context
def shift(ctx, bits):
    from .commands import cmd_quant_shift

    repo = ctx.obj
    cmd_quant_shift(repo, bits)
    click.echo("Shift quantization")


@main.group(help="Simulation")
def sim():
    pass


@sim.command(name="file", help="Simulation using file")
@click.option(
    "--feature",
    "-f",
    default=example_path() / "karatsuba032.jpg",
    help="Feature file, can be a image or json list file.",
)
@click.option(
    "--weight",
    "-w",
    default=example_path() / "laplace.json",
    help="Weight file, need to be a json list file.",
)
@click.option("--name", "-n", default="", help="Suffix of output file name.")
@click.option(
    "--standard", "-s", is_flag=True, default=False, help="Standar convolution."
)
@click.pass_context
def sim_file(ctx, feature, weight, name, standard):
    from .commands import cmd_sim_file

    repo = ctx.obj
    output = cmd_sim_file(repo, feature, weight, name, standard)
    ctx.exit(0)
    click.echo(output["text"])


@sim.command(name="rand", help="Simulation with random numbers")
@click.option(
    "--image-side", "-i", default=32, help="Image side, must be a power of two."
)
@click.option(
    "--loop", "-L", default=1, help="Total of execution loops. Not implemented"
)
@click.option(
    "--feature",
    "-f",
    nargs=2,
    default=[0, 127],
    help="Minimal and maximal value of feature random data.",
)
@click.option(
    "--weight",
    "-w",
    nargs=2,
    default=[0, 127],
    help="Minimal and maximal value of weight random data.",
)
@click.option("--name", "-n", default="", help="Suffix of output file name.")
@click.option(
    "--seed", "-d", default=0, help="Seed to random number generator."
)
@click.option(
    "--standard", "-s", is_flag=True, default=False, help="Standar convolution."
)
@click.pass_context
def sim_rand(ctx, feature, weight, image_side, loop, name, seed, standard):
    from .commands import cmd_sim_random

    repo = ctx.obj
    output = cmd_sim_random(
        repo, feature, weight, image_side, loop, name, seed, standard
    )
    ctx.exit(0)
    click.echo(output["text"])


@sim.command(name="seq", help="Simulation with sequential numbers")
@click.option(
    "--image-side", "-i", default=32, help="Image side, must be a power of two."
)
@click.option(
    "--feature",
    "-f",
    default=0,
    help="Start value of feature sequential data.",
)
@click.option(
    "--weight",
    "-w",
    default=0,
    help="Start value of weight sequential data.",
)
@click.option("--suffix", "-x", default="", help="Suffix of output file name.")
@click.option(
    "--standard", "-s", is_flag=True, default=False, help="Standar convolution."
)
@click.pass_context
def sim_seq(ctx, feature, weight, image_side, suffix, standard):
    from .commands import cmd_sim_seq

    repo = ctx.obj
    output = cmd_sim_seq(repo, feature, weight, image_side, suffix, standard)
    ctx.exit(0)
    click.echo(output["text"])


@main.group(help="Create example")
def example():
    pass


@example.command(name="rand", help="Example with random numbers")
@click.option(
    "--feature",
    "-f",
    nargs=2,
    default=[0, 127],
    help="Minimal and maximal value of feature random data.",
)
@click.option(
    "--weight",
    "-w",
    nargs=2,
    default=[0, 127],
    help="Minimal and maximal value of weight random data.",
)
@click.option("--suffix", "-x", default="", help="Suffix of output file name.")
@click.option("--quant", "-q", is_flag=True, default=False)
@click.pass_context
def ex_rand(ctx, feature, weight, suffix, quant):
    from .commands import cmd_example_random

    repo = ctx.obj
    cmd_example_random(repo, feature, weight, suffix, quant)
    click.echo("Random example")


@example.command(name="seq", help="Example with sequential numbers")
@click.option(
    "--feature",
    "-f",
    default=0,
    help="Minimal value of sequential feature data.",
)
@click.option(
    "--weight", "-w", default=0, help="Minimal value of sequential weight data."
)
@click.option("--suffix", "-x", default="", help="Suffix of output file name.")
@click.option("--quant", "-q", is_flag=True, default=False)
@click.pass_context
def ex_seq(ctx, feature, weight, suffix, quant):
    from .commands import cmd_example_sequential

    repo = ctx.obj
    cmd_example_sequential(repo, feature, weight, suffix, quant)
    click.echo("Sequential example")


@example.command(name="list", help="Example from list of numbers")
@click.option(
    "--feature",
    "-f",
    type=str,
    help="List of features.",
)
@click.option("--weight", "-w", type=str, help="List of weights.")
@click.option("--suffix", "-x", default="", help="Suffix of output file name.")
@click.option("--quant", "-q", is_flag=True, default=False)
@click.pass_context
def ex_list(ctx, feature, weight, suffix, quant):
    from .commands import cmd_example_list

    repo = ctx.obj
    cmd_example_list(
        repo,
        list(map(int, feature.split(","))),
        list(map(int, weight.split(","))),
        suffix,
        quant,
    )
    click.echo("Sequential example")


if __name__ == "__main__":
    main()
