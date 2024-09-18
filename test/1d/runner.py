import json
from pathlib import Path

from click.testing import CliRunner

from src.fast_convolution import cli


root = Path(__file__).parent.resolve()

with open(root / "cmd.json") as f:
    cmd_dict = json.load(f)


def test_init1d():
    runner = CliRunner()
    result = runner.invoke(cli.main, cmd_dict["init"])
    assert result.exit_code == 0


def test_build_toom_cook1d():
    runner = CliRunner()
    result = runner.invoke(cli.main, cmd_dict["build"])
    assert result.exit_code == 0


def test_example_sequential():
    runner = CliRunner()
    result = runner.invoke(cli.main, cmd_dict["example_seq"])
    assert result.exit_code == 0


def test_sim_file():
    runner = CliRunner()
    result = runner.invoke(cli.main, cmd_dict["sim_file"])
    assert result.exit_code == 0
