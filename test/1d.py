import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from fast_convolution import cli

from .conftest import file_list
from .lib import run

# @pytest.fixture(scope="session")
# def file(pytestconfig):
#     return pytestconfig.getoption("file")


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


root = Path(__file__).parent.resolve()

with open(root / "json/cmd_common.json") as f:
    cmd_common_dict = json.load(f)

list_repo_path = [root / (Path(f).stem) for f in file_list]
list_repo_opt = [["-p", f.as_posix()] for f in list_repo_path]

list_cmd_dict = [
    read_json(root / "json" / (f.stem + ".json")) for f in list_repo_path
]

list_args = [
    (x, y, z) for x, y, z in zip(list_repo_path, list_repo_opt, list_cmd_dict)
]


@pytest.mark.parametrize("args", list_args)
def test_rm(args):
    repo_path, repo_opt, cmd_dict = args
    shutil.rmtree(repo_path, ignore_errors=True)


@pytest.mark.parametrize("args", list_args)
@pytest.mark.parametrize("cmd", ["init", "build"])
def test_project(args, cmd):
    repo_path, repo_opt, cmd_dict = args
    run(cmd, repo_path, repo_opt, cmd_dict)


# @pytest.mark.parametrize("args", list_args)
# def test_init(args):
#     repo_path, repo_opt, cmd_dict = args
#     run("init", repo_path, repo_opt, cmd_dict)


# @pytest.mark.parametrize("args", list_args)
# def test_build(args):
#     repo_path, repo_opt, cmd_dict = args
#     run("build", repo_path, repo_opt, cmd_dict)


# def test_bind(args):
#     repo_path, repo_opt, cmd_dict = args
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_dict["bind"])
#     assert result.exit_code == 0


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
