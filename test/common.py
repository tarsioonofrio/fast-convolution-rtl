import json
from pathlib import Path

import pytest

from .conftest import file_list1d, file_list2d
from .lib import read_json, run

root = Path(__file__).parent.resolve()

with open(root / "json/cmd_common.json") as f:
    cmd_common_dict = json.load(f)

list_cmd = [
    "ex_rand",
    "ex_seq",
    "sim_rand",
    "sim_file",
    "quant",
    "sim_rand_quant",
    "sim_file_quant",
]

list_repo_path = [
    root / (Path(f).stem) for ll in [file_list1d, file_list2d] for f in ll
]
list_repo_opt = [["-p", f.as_posix()] for f in list_repo_path]

list_cmd_dict = [
    read_json(root / "json" / (f.stem + ".json")) for f in list_repo_path
]

list_args = [
    (x, y, z) for x, y, z in zip(list_repo_path, list_repo_opt, list_cmd_dict)
]


# @pytest.mark.parametrize("args", list_args)
# @pytest.mark.parametrize("cmd", list_cmd)
# def test_project(args, cmd):
#     repo_path, repo_opt, _ = args
#     run(cmd, repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_ex_rand(args):
    repo_path, repo_opt, cmd_dict = args
    run("ex_rand", repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_ex_seq(args):
    repo_path, repo_opt, cmd_dict = args
    run("ex_seq", repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_sim_rand(args):
    repo_path, repo_opt, cmd_dict = args
    run("sim_rand", repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_sim_file(args):
    repo_path, repo_opt, cmd_dict = args
    run("sim_file", repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_quant(args):
    repo_path, repo_opt, cmd_dict = args
    run("quant", repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_sim_rand_quant(args):
    repo_path, repo_opt, cmd_dict = args
    run("sim_rand_quant", repo_path, repo_opt, cmd_common_dict)


@pytest.mark.parametrize("args", list_args)
def test_sim_file_quant(args):
    repo_path, repo_opt, cmd_dict = args
    run("sim_file_quant", repo_path, repo_opt, cmd_common_dict)
