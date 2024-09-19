#!/usr/bin/env python

"""Tests for `fast_convolution` package."""

import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).parent.resolve()
repo_path = root / "repo"

cmd_lst = ['fast-conv', '-p', './repo']

with open(root / "cmd.json") as f:
    cmd_dict = json.load(f)


def subprocess_test(cmd):
    return subprocess.run(cmd, capture_output=True, cwd=root)


def test_init():
    shutil.rmtree(repo_path, ignore_errors=True)
    result = subprocess_test(cmd_lst + cmd_dict["init"])
    assert result.returncode == 0, result.stderr


def test_build():
    result = subprocess_test(cmd_lst + cmd_dict["build"])
    assert result.returncode == 0


def test_bind():
    result = subprocess_test(cmd_lst + cmd_dict["bind"])
    assert result.returncode == 0


def test_quant():
    result = subprocess_test(cmd_lst + cmd_dict["quant"])
    assert result.returncode == 0


def test_ex_rand():
    result = subprocess_test(cmd_lst + cmd_dict["ex_rand"])
    assert result.returncode == 0


def test_ex_seq():
    result = subprocess_test(cmd_lst + cmd_dict["ex_seq"])
    assert result.returncode == 0


def test_sim_rand():
    result = subprocess_test(cmd_lst + cmd_dict["sim_rand"])
    assert result.returncode == 0


def test_sim_file():
    result = subprocess_test(cmd_lst + cmd_dict["sim_file"])
    assert result.returncode == 0

# def test_show():
#     result = subprocess_test(['show'])
#     assert result.returncode == 0

