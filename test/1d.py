import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from fast_convolution import cli

from .conftest import file_list

# @pytest.fixture(scope="session")
# def file(pytestconfig):
#     return pytestconfig.getoption("file")


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)


root = Path(__file__).parent.resolve()

open(root / "json/cmd_common.json")

with open(root / "json/cmd_common.json") as f:
    cmd_common_dict = json.load(f)

list_repo_path = [root / (Path(f).stem) for f in file_list]
list_repo_opt = [["-p", f.as_posix()] for f in list_repo_path]

# with open(root / "json" / Path(__file__).with_suffix(".json").name) as f:
#     cmd_dict = json.load(f)

list_cmd_dict = [
    read_json(root / "json" / (f.stem + ".json")) for f in list_repo_path
]

list_args = [
    (x, y, z) for x, y, z in zip(list_repo_path, list_repo_opt, list_cmd_dict)
]

@pytest.mark.parametrize("args", list_args)
def test_init(args):
    repo_path, repo_opt, cmd_dict = args
    shutil.rmtree(repo_path, ignore_errors=True)
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["init"])
    assert result.exit_code == 0


@pytest.mark.parametrize("args", list_args)
def test_build(args):
    print(args)
    repo_path, repo_opt, cmd_dict = args
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["build"])
    assert result.exit_code == 0


# def test_bind():
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_dict["bind"])
#     assert result.exit_code == 0


# def test_ex_rand():
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_common_dict["ex_rand"])
#     assert result.exit_code == 0


# def test_ex_seq():
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_common_dict["ex_seq"])
#     assert result.exit_code == 0


# def test_sim_rand():
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_common_dict["sim_rand"])
#     assert result.exit_code == 0


# def test_sim_file():
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_common_dict["sim_file"])
#     assert result.exit_code == 0


# def test_quant():
#     runner = CliRunner()
#     result = runner.invoke(cli.main, repo_opt + cmd_common_dict["quant"])
#     assert result.exit_code == 0


# def test_sim_rand_quant():
#     runner = CliRunner()
#     result = runner.invoke(
#         cli.main, repo_opt + cmd_common_dict["sim_rand_quant"]
#     )
#     assert result.exit_code == 0


# def test_sim_file_quant():
#     runner = CliRunner()
#     result = runner.invoke(
#         cli.main, repo_opt + cmd_common_dict["sim_file_quant"]
#     )
#     assert result.exit_code == 0
