import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from fast_convolution import cli


root = Path(__file__).parent.resolve()
repo_path = root / "repo"
repo_opt = ["-p", repo_path.as_posix()]

with open(root / "cmd.json") as f:
    cmd_dict = json.load(f)


def test_init():
    shutil.rmtree(repo_path, ignore_errors=True)
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["init"])
    assert result.exit_code == 0


def test_build():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["build"])
    assert result.exit_code == 0


def test_bind():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["bind"])
    assert result.exit_code == 0


def test_quant():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["quant"])
    assert result.exit_code == 0


def test_example_rand():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["ex_rand"])
    assert result.exit_code == 0


def test_example_seq():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["ex_seq"])
    assert result.exit_code == 0


def test_sim_rand():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["sim_rand"])
    assert result.exit_code == 0


def test_sim_file():
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict["sim_file"])
    assert result.exit_code == 0
