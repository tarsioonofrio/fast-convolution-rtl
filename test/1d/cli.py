#!/usr/bin/env python

"""Tests for `fast_convolution` package."""

import shutil
import subprocess
from pathlib import Path

root = Path(__file__).parent.resolve()


def test_init():
    shutil.rmtree(root / "repo", ignore_errors=True)
    result = subprocess.run(
        ['fast-conv', '-p', './repo', '-p', './repo', 'init', '1d', '-o', '3'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0, result.stderr


def test_build_toomcook():
    result = subprocess.run(
        ['fast-conv', '-p', './repo', 'build', '1d', 'toom-cook'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_quant_shift():
    result = subprocess.run(
        ['fast-conv', '-p', './repo', 'quant', 'shift', '-b', '4'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_example_rand():
    result = subprocess.run(
        ['fast-conv', '-p', './repo', 'example', 'rand'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_example_seq():
    result = subprocess.run(
        ['fast-conv', '-p', './repo', 'example', 'seq'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_sim_rand():
    result = subprocess.run(
        ['fast-conv', '-p', './repo', 'sim', ' rand'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_sim_file():
    result = subprocess.run(
        ['fast-conv', '-p', './repo', 'sim', 'file'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


# def test_show():
#     result = subprocess.run(
#         ['fast-conv', '-p', './repo', 'show'],
#         capture_output=True,
#         cwd=root
#     )
#     assert result.returncode == 0

