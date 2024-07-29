from pathlib import Path

import pytest
from click.testing import CliRunner

from fast_convolution import cli, utils


root = Path(__file__).parent.parent.parent.resolve()


def mock_getcwd1d():
    return root / "test_1d"


def mock_getcwd2d():
    return root / "test_2d"


def test_bind_nest(monkeypatch):
    # mocker.patch('fast_convolution.utils', 'getcwd', mock_getcwd2d)
    runner = CliRunner()
    # monkeypatch.chdir(root / "test_2d")
    # monkeypatch.setattr("os.getcwd", mock_getcwd2d)
    result = runner.invoke(cli.nest)
    assert result.exit_code == 0


def test_example_sequential(monkeypatch):
    # mocker.patch('fast_convolution.utils', 'getcwd', mock_getcwd2d)
    runner = CliRunner()
    # monkeypatch.chdir(root / "test_2d")
    # monkeypatch.setattr("os.getcwd", mock_getcwd2d)
    result = runner.invoke(cli.seq)
    assert result.exit_code == 0
