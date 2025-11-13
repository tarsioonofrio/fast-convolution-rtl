#!/usr/bin/env python

import argparse
import os
import sys
import traceback
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

try:
    import ipdb as pdb
except ModuleNotFoundError:  # pragma: no cover - fallback when ipdb missing
    import pdb

from .commands import (
    cmd_build2d_bind_kron,
    cmd_build2d_bind_nest,
    cmd_build_manual_factorization1d,
    cmd_build_manual_factorization2d,
    cmd_build_toom_cook1d,
    cmd_build_toom_cook2d,
    cmd_example_list,
    cmd_example_random,
    cmd_example_sequential,
    cmd_init,
    cmd_quant_none,
    cmd_quant_shift,
    cmd_sim_file,
    cmd_sim_int,
    cmd_sim_normal,
)
from .config import (
    default_toom_cook_points1d,
    default_toom_cook_points2d,
    num_points1d,
    num_points2d,
    read_init_if_exists,
)
from .repo import Repo


def excepthook(exc_type, value, tb):
    """Drop into ipdb whenever an uncaught exception happens."""
    traceback.print_exception(exc_type, value, tb)
    pdb.post_mortem(tb)


sys.excepthook = excepthook


def example_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "images"


def _ensure_sequence(value: Union[Sequence, int, str]) -> List:
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _require_points(
    points: Optional[Sequence[str]],
    expected: int,
    label: str,
) -> List[str]:
    if points is None:
        return []
    if expected > 0 and len(points) != expected:
        raise SystemExit(f"{label} expects {expected} values, got {len(points)}")
    return list(points)


def _comma_separated_to_ints(values: str) -> List[int]:
    return [int(item.strip()) for item in values.split(",") if item.strip()]


def handle_init_1d(args):
    message = cmd_init(args.repo, 1, args.in_len, args.out_len, args.kernel)
    if message is not None:
        print(message)
    return 0


def handle_init_2d(args):
    message = cmd_init(args.repo, 2, args.in_len, args.out_len, args.kernel)
    if message is not None:
        print(message)
    return 0


def handle_build_toom_cook1d(args):
    init_data = read_init_if_exists(args.repo)
    size = init_data.get("c", 1)
    expected = num_points1d(size)
    points = _require_points(args.points, expected, "--points")
    if not points:
        default_points = _ensure_sequence(default_toom_cook_points1d(size))
        points = [str(p) for p in default_points]
    cmd_build_toom_cook1d(args.repo, points)
    print("Build 1D Toom Cook")
    return 0


def handle_build_manual1d(args):
    cmd_build_manual_factorization1d(args.repo)
    print("Build 1D manual factorization")
    return 0


def handle_build_toom_cook2d(args):
    init_data = read_init_if_exists(args.repo)
    size = init_data.get("c", 1)
    expected_first = num_points2d(size, 0)
    expected_second = num_points2d(size, 1)

    points_1d = _require_points(args.points_1d, expected_first, "--points-1d/--p1")
    points_2d = _require_points(args.points_2d, expected_second, "--points-2d/--p2")
    if not points_1d:
        default_first = _ensure_sequence(default_toom_cook_points2d(size, 0))
        points_1d = [str(p) for p in default_first]
    if not points_2d:
        default_second = _ensure_sequence(default_toom_cook_points2d(size, 1))
        points_2d = [str(p) for p in default_second]

    cmd_build_toom_cook2d(args.repo, points_1d, points_2d)
    print("Build 2D Toom Cook dimension.")
    return 0


def handle_build_manual2d(args):
    cmd_build_manual_factorization2d(args.repo)
    print("Build 2D manual factorization")
    return 0


def handle_bind_nest(args):
    cmd_build2d_bind_nest(args.repo)
    return 0


def handle_bind_kron(args):
    cmd_build2d_bind_kron(args.repo)
    return 0


def handle_quant_none(args):
    cmd_quant_none(args.repo)
    return 0


def handle_quant_shift(args):
    cmd_quant_shift(args.repo, args.bits)
    print("Shift quantization")
    return 0


def handle_sim_file(args):
    output = cmd_sim_file(
        args.repo,
        args.feature,
        args.weight,
        args.name,
        args.standard,
    )
    if isinstance(output, dict) and "text" in output:
        print(output["text"])
    return 0


def handle_sim_int(args):
    output = cmd_sim_int(
        args.repo,
        args.feature,
        args.weight,
        args.channel_in,
        args.channel_out,
        args.random,
        args.image_side,
        args.name,
        args.seed,
        args.bias,
        args.standard,
    )
    if isinstance(output, dict) and "text" in output:
        print(output["text"])
    return 0


def handle_sim_normal(args):
    output = cmd_sim_normal(
        args.repo,
        args.image_side,
        args.channel_in,
        args.channel_out,
        args.name,
        args.seed,
        args.bias,
        args.standard,
    )
    if isinstance(output, dict) and "text" in output:
        print(output["text"])
    return 0


def handle_example_rand(args):
    cmd_example_random(args.repo, args.feature, args.weight, args.suffix, args.quant)
    print("Random example")
    return 0


def handle_example_seq(args):
    cmd_example_sequential(args.repo, args.feature, args.weight, args.suffix, args.quant)
    print("Sequential example")
    return 0


def handle_example_list(args):
    if args.feature is None or args.weight is None:
        raise SystemExit("--feature and --weight are required")
    feature_values = _comma_separated_to_ints(args.feature)
    weight_values = _comma_separated_to_ints(args.weight)
    cmd_example_list(args.repo, feature_values, weight_values, args.suffix, args.quant)
    print("Sequential example")
    return 0


def _build_init_parser(subparsers):
    init_help = (
        "Size of two vectors to be convoluted. The two sizes must be in "
        "format Out = In - W + 1 or In = Out + W - 1 where In is the number of "
        "elements in the input, Out is the number of elements in the output, "
        "and W is the number of elements of weights or kernel."
    )
    init_parser = subparsers.add_parser("init", help="Initialize fast convolution repo.", description=init_help)
    init_sub = init_parser.add_subparsers(dest="init_command", metavar="subcommand")
    init_sub.required = True

    init_1d = init_sub.add_parser("1d", help="Initialize 1D configuration.")
    init_1d.add_argument("-i", "--in-len", type=int, default=None, help="Input length.")
    init_1d.add_argument("-o", "--out-len", type=int, default=None, help="Output length.")
    init_1d.add_argument("-w", "--kernel", type=int, default=3, help="Kernel size (default: 3).")
    init_1d.set_defaults(func=handle_init_1d)

    init_2d = init_sub.add_parser("2d", help="Initialize 2D configuration.")
    init_2d.add_argument("-i", "--in-len", type=int, default=None, help="Input length.")
    init_2d.add_argument("-o", "--out-len", type=int, default=None, help="Output length.")
    init_2d.add_argument("-w", "--kernel", type=int, default=3, help="Kernel size (default: 3).")
    init_2d.set_defaults(func=handle_init_2d)


def _build_1d_build_parser(build_sub):
    build_1d = build_sub.add_parser("1d", help="1D build commands.")
    build_1d_sub = build_1d.add_subparsers(dest="build_1d_command", metavar="command")
    build_1d_sub.required = True

    toom_cook = build_1d_sub.add_parser("toom-cook", help="Build 1D Toom-Cook interpolation.")
    toom_cook.add_argument(
        "--points",
        "-p",
        nargs="+",
        default=None,
        help="List of points to interpolate for Toom-Cook.",
    )
    toom_cook.set_defaults(func=handle_build_toom_cook1d)

    manual = build_1d_sub.add_parser("manual", help="Build 1D manual factorization (6 multiplications).")
    manual.set_defaults(func=handle_build_manual1d)


def _build_2d_build_parser(build_sub):
    build_2d = build_sub.add_parser("2d", help="2D build commands.")
    build_2d_sub = build_2d.add_subparsers(dest="build_2d_command", metavar="command")
    build_2d_sub.required = True

    toom_cook = build_2d_sub.add_parser("toom-cook", help="Build 2D Toom-Cook interpolation.")
    toom_cook.add_argument(
        "--points-1d",
        "--p1",
        nargs="+",
        default=None,
        dest="points_1d",
        help="List of points for Toom-Cook first dimension.",
    )
    toom_cook.add_argument(
        "--points-2d",
        "--p2",
        nargs="+",
        default=None,
        dest="points_2d",
        help="List of points for Toom-Cook second dimension.",
    )
    toom_cook.set_defaults(func=handle_build_toom_cook2d)

    manual = build_2d_sub.add_parser("manual", help="Build 2D manual factorization (6x6 multiplications).")
    manual.set_defaults(func=handle_build_manual2d)

    bind = build_2d_sub.add_parser("bind", help="Bind multiple dimensions.")
    bind_sub = bind.add_subparsers(dest="bind_command", metavar="method")
    bind_sub.required = True

    nest = bind_sub.add_parser("nest", help="Nested multidimensional bind.")
    nest.set_defaults(func=handle_bind_nest)

    kron = bind_sub.add_parser("kron", help="Kronecker multidimensional bind.")
    kron.set_defaults(func=handle_bind_kron)


def _build_build_parser(subparsers):
    build_parser = subparsers.add_parser("build", help="Build fast convolution.")
    build_sub = build_parser.add_subparsers(dest="build_dimension", metavar="dimension")
    build_sub.required = True

    _build_1d_build_parser(build_sub)
    _build_2d_build_parser(build_sub)


def _build_quant_parser(subparsers):
    quant_parser = subparsers.add_parser("quant", help="Quantization configuration.")
    quant_sub = quant_parser.add_subparsers(dest="quant_command", metavar="command")
    quant_sub.required = True

    none = quant_sub.add_parser("none", help="Set quantization to none.")
    none.set_defaults(func=handle_quant_none)

    shift = quant_sub.add_parser("shift", help="Shift quantization.")
    shift.add_argument("-b", "--bits", type=int, default=4, help="Number of bits to shift (default: 4).")
    shift.set_defaults(func=handle_quant_shift)


def _build_sim_parser(subparsers):
    sim_parser = subparsers.add_parser("sim", help="Simulation helpers.")
    sim_sub = sim_parser.add_subparsers(dest="sim_command", metavar="command")
    sim_sub.required = True

    sim_file = sim_sub.add_parser("file", help="Simulation using input files.")
    sim_file.add_argument(
        "-f",
        "--feature",
        type=Path,
        default=example_path() / "karatsuba032.jpg",
        help="Feature file (image or JSON list).",
    )
    sim_file.add_argument(
        "-w",
        "--weight",
        type=Path,
        default=example_path() / "laplace.json",
        help="Weight JSON file.",
    )
    sim_file.add_argument("-n", "--name", default="", help="Suffix of output file name.")
    sim_file.add_argument("-s", "--standard", action="store_true", help="Use standard convolution.")
    sim_file.set_defaults(func=handle_sim_file)

    sim_int = sim_sub.add_parser("int", help="Simulation with integers.")
    sim_int.add_argument("--image-side", type=int, default=32, help="Image side length.")
    sim_int.add_argument("-f", "--feature", type=int, default=0, help="Minimal value of feature.")
    sim_int.add_argument("-w", "--weight", type=int, default=0, help="Minimal value of kernel.")
    sim_int.add_argument("-i", "--channel-in", type=int, default=1, help="Channel input size.")
    sim_int.add_argument("-o", "--channel-out", type=int, default=1, help="Channel output size.")
    sim_int.add_argument("-r", "--random", action="store_true", help="Use random integers.")
    sim_int.add_argument("-n", "--name", default="", help="Suffix of output file name.")
    sim_int.add_argument("-d", "--seed", type=int, default=0, help="Seed for random number generator.")
    sim_int.add_argument(
        "-b",
        "--bias",
        type=int,
        default=None,
        help="Minimal bias value per output channel (omit to disable bias).",
    )
    sim_int.add_argument("-s", "--standard", action="store_true", help="Use standard convolution.")
    sim_int.set_defaults(func=handle_sim_int)

    sim_normal = sim_sub.add_parser(
        "normal",
        help="Simulation with normal distribution (mean 0, std 1).",
    )
    sim_normal.add_argument("--image-side", type=int, default=32, help="Image side length.")
    sim_normal.add_argument("-n", "--name", default="", help="Suffix of output file name.")
    sim_normal.add_argument("-i", "--channel-in", type=int, default=1, help="Channel input size.")
    sim_normal.add_argument("-o", "--channel-out", type=int, default=1, help="Channel output size.")
    sim_normal.add_argument("-d", "--seed", type=int, default=0, help="Seed for random number generator.")
    sim_normal.add_argument(
        "-b",
        "--bias",
        type=float,
        default=None,
        help="Mean of the normal distribution used to sample bias (omit to disable bias).",
    )
    sim_normal.add_argument("-s", "--standard", action="store_true", help="Use standard convolution.")
    sim_normal.set_defaults(func=handle_sim_normal)


def _build_example_parser(subparsers):
    example_parser = subparsers.add_parser("example", help="Create examples.")
    example_sub = example_parser.add_subparsers(dest="example_command", metavar="command")
    example_sub.required = True

    rand = example_sub.add_parser("rand", help="Example with random numbers.")
    rand.add_argument(
        "-f",
        "--feature",
        nargs=2,
        type=int,
        default=[0, 127],
        metavar=("MIN", "MAX"),
        help="Range of feature random data.",
    )
    rand.add_argument(
        "-w",
        "--weight",
        nargs=2,
        type=int,
        default=[0, 127],
        metavar=("MIN", "MAX"),
        help="Range of weight random data.",
    )
    rand.add_argument("-x", "--suffix", default="", help="Suffix of output file name.")
    rand.add_argument("-q", "--quant", action="store_true", help="Use quantized representation.")
    rand.set_defaults(func=handle_example_rand)

    seq = example_sub.add_parser("seq", help="Example with sequential numbers.")
    seq.add_argument("-f", "--feature", type=int, default=0, help="Minimal value of sequential feature data.")
    seq.add_argument("-w", "--weight", type=int, default=0, help="Minimal value of sequential weight data.")
    seq.add_argument("-x", "--suffix", default="", help="Suffix of output file name.")
    seq.add_argument("-q", "--quant", action="store_true", help="Use quantized representation.")
    seq.set_defaults(func=handle_example_seq)

    lst = example_sub.add_parser("list", help="Example from list of numbers.")
    lst.add_argument("-f", "--feature", type=str, help="Comma separated list of features.")
    lst.add_argument("-w", "--weight", type=str, help="Comma separated list of weights.")
    lst.add_argument("-x", "--suffix", default="", help="Suffix of output file name.")
    lst.add_argument("-q", "--quant", action="store_true", help="Use quantized representation.")
    lst.set_defaults(func=handle_example_list)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fast-convolution",
        description="Command line interface for fast convolution utilities.",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=os.environ.get("PATH_REPO", "."),
        help="Path to the repository root (defaults to current directory or PATH_REPO).",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    _build_init_parser(subparsers)
    _build_build_parser(subparsers)
    _build_quant_parser(subparsers)
    _build_sim_parser(subparsers)
    _build_example_parser(subparsers)

    return parser


def main(argv: Optional[Iterable[str]] = None):
    parser = create_parser()
    args = parser.parse_args(argv)
    args.repo = Repo(args.path)

    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args) or 0


if __name__ == "__main__":
    raise SystemExit(main())
