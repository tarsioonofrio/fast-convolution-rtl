#!/usr/bin/env python

"""Tests for `fast_convolution` package."""

import pytest
import shutil
import subprocess
from pathlib import Path


root = Path(__file__).parent.parent.parent.resolve()


tmp_dir1 = root / "test_1d"
tmp_dir2 = root / "test_2d"


def test_init1d():
    shutil.rmtree(tmp_dir1)
    tmp_dir1.mkdir(parents=True)
    result = subprocess.run(
        ['fast-conv', 'init', '1d', '-o', '3'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_init2d():
    shutil.rmtree(tmp_dir2)
    tmp_dir2.mkdir(parents=True)
    result = subprocess.run(
        ['fast-conv', 'init', '2d', '-o', '3', '3'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_build_1d_toomcook():
    result = subprocess.run(
        ['fast-conv', 'build', '1d', 'toom-cook'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_build_2d_toom_cook():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'toom-cook'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_build_2d_bind_iterate():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'bind', 'iter'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_build_2d_bind_nest():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'bind', 'nest'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_quant_1d_shift():
    result = subprocess.run(
        ['fast-conv', 'quant', 'shift'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_quant_2d_shift():
    result = subprocess.run(
        ['fast-conv', 'quant', 'shift'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_example_1d_seq():
    result = subprocess.run(
        ['fast-conv', 'example', 'seq'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_example_1d_rand():
    result = subprocess.run(
        ['fast-conv', 'example', ' rand'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_example_2d_seq():
    result = subprocess.run(
        ['fast-conv', 'example', 'seq'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_example_2d_rand():
    result = subprocess.run(
        ['fast-conv', 'example', ' rand'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_sim_1d_file():
    result = subprocess.run(
        ['fast-conv', 'sim', 'file'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_sim_1d_rand():
    result = subprocess.run(
        ['fast-conv', 'sim', ' rand'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_sim_2d_file():
    result = subprocess.run(
        ['fast-conv', 'sim', 'file'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_sim_2d_rand():
    result = subprocess.run(
        ['fast-conv', 'sim', ' rand'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_show_1d():
    result = subprocess.run(
        ['fast-conv', 'show'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_show_2d():
    result = subprocess.run(
        ['fast-conv', 'show'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0
