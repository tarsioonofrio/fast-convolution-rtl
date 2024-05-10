#!/usr/bin/env python

"""Tests for `fast_convolution` package."""

import os
# import pytest
import shutil
import subprocess
from pathlib import Path

from fast_convolution import cli, commands

root = Path(__file__).parent.parent.parent.resolve()


tmp_dir1 = root / "test_1d"
shutil.rmtree(tmp_dir1)
tmp_dir1.mkdir(parents=True)
tmp_dir2 = root / "test_2d"
shutil.rmtree(tmp_dir2)
tmp_dir2.mkdir(parents=True)


def test_init1d():
    result = subprocess.run(
        ['fast-conv', 'init', '1d', '-o', '3'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_build_1d_toomcook():
    result = subprocess.run(
        ['fast-conv', 'build', '1d', 'toom-cook'],
        capture_output=True,
        cwd=tmp_dir1
    )
    assert result.returncode == 0


def test_init2d():
    result = subprocess.run(
        ['fast-conv', 'init', '2d', '-o', '3', '3'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0


def test_build_2d_toom_cook():
    result = subprocess.run(
        ['fast-conv', 'build', '2d', 'toom-cook'],
        capture_output=True,
        cwd=tmp_dir2
    )
    assert result.returncode == 0

