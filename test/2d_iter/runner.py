from pathlib import Path

import pytest
from click.testing import CliRunner

from src.fast_convolution import cli, utils


root = Path(__file__).parent.resolve()


def test_bind_nest():
    runner = CliRunner()
    result = runner.invoke(cli.nest)
    assert result.exit_code == 0


def test_example_sequential():
    runner = CliRunner()
    result = runner.invoke(cli.seq)
    # with runner.isolated_filesystem(temp_dir=root) as td:
    #     result = runner.invoke(cli.seq)
    #     assert result.exit_code == 0


def test_bind_nest():
    runner = CliRunner()
    result = runner.invoke(cli.nest)
    assert result.exit_code == 0


def test_sim_file():
    runner = CliRunner()
    result = runner.invoke(cli.sim)
    assert result.exit_code == 0
