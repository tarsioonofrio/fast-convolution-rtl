from pathlib import Path

import pytest


root = Path(__file__).parent.resolve()
example_path = Path(__file__).resolve().parent.parent.parent / "images"


def test_bind_iterate():
    from fast_convolution.commands import cmd_build2d_bind_iterate
    cmd_build2d_bind_iterate()


def test_bind_nest():
    from fast_convolution.commands import cmd_build2d_bind_nest
    cmd_build2d_bind_nest()


def test_example_seq():
    from fast_convolution.commands import cmd_example_sequential
    cmd_example_sequential(0, 0)


def test_sim_file():
    from fast_convolution.commands import cmd_sim_file
    feature = example_path / "karatsuba032.jpg"
    weight = example_path / "laplace.json"
    cmd_sim_file(feature, weight)
