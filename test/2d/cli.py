#!/usr/bin/env python

"""Tests for `fast_convolution` package."""

import pytest
import shutil
import subprocess
from pathlib import Path


root = Path(__file__).parent.resolve()
tmp_dir = [
    root / "build",
    root / "clib",
    root / "config",
    root / "example",
    root / "sim",
]
# name_file = Path(__file__).stem
# tmp_dir = root / name_file



def test_init():
    for d in tmp_dir:
        shutil.rmtree(d, ignore_errors=True)
    result = subprocess.run(
        ['fast-conv', 'init', '2d', '-o', '3', '3'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_build_toom_cook():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'toom-cook'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_build_bind_iterate():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'bind', 'iter'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_build_bind_nest():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'bind', 'nest'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_quant_shift():
    result = subprocess.run(
        ['fast-conv', 'quant', 'shift', '-b', '4'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_example_seq():
    result = subprocess.run(
        ['fast-conv', 'example', 'seq'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_example_rand():
    result = subprocess.run(
        ['fast-conv', 'example', ' rand'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_sim_file():
    result = subprocess.run(
        ['fast-conv', 'sim', 'file'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_sim_rand():
    result = subprocess.run(
        ['fast-conv', 'sim', ' rand'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0


def test_show():
    result = subprocess.run(
        ['fast-conv', 'show'],
        capture_output=True,
        cwd=root
    )
    assert result.returncode == 0
