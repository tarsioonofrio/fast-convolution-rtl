import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from fast_convolution import cli, commands
from fast_convolution.repo import Repo

repo_name = "2d2_iter"
function_name = "test_bind"

root = Path(__file__).parent.parent.resolve() / "test"
file_path = root / f"{repo_name}.py"
repo_path = root / repo_name


commands.cmd_build2d_bind_iterate(Repo(repo_path))
