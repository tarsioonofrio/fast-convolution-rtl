import json
# import shutil
from pathlib import Path

from click.testing import CliRunner

from fast_convolution import cli


repo_name = "2d2_nest"
function = "ex_seq"

root = Path(__file__).parent.parent.resolve() / "test" / repo_name

repo_path = root / "repo"
repo_opt = ["-p", repo_path.as_posix()]

with open(root.parent / "cmd_common.json") as f:
    cmd_common_dict = json.load(f)

with open(root / "cmd.json") as f:
    cmd_dict = json.load(f)


def init():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["init"])
    print(result.exit_code)


def build():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["build"])
    print(result.exit_code)


def bind():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["bind"])
    print(result.exit_code)


def ex_rand():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["ex_rand"])
    print(result.exit_code)


def ex_seq():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["ex_seq"])
    print(result.exit_code)


def sim_rand():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["sim_rand"])
    print(result.exit_code)


def sim_file():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["sim_file"])
    print(result.exit_code)


def quant():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["quant"])
    print(result.exit_code)


def sim_rand_quant():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["sim_rand_quant"])
    print(result.exit_code)


def sim_file_quant():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_common_dict["sim_file_quant"])
    print(result.exit_code)


if __name__ == '__main__':
    locals()[function]()
