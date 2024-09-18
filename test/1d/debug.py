from pathlib import Path

from click.testing import CliRunner

from src.fast_convolution import cli


runner = CliRunner()
result = runner.invoke(cli.toom_cook1d)
