import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from fast_convolution import cli


repo_name = "2d2_iter"
function_name = "test_bind"

root = Path(__file__).parent.parent.resolve() / "test"
file_path = root / f"{repo_name}.py"
repo_path = root / repo_name
repo_opt = ["-p", repo_path.as_posix()]


with open(root / "json/cmd_common.json") as f:
    cmd_common_dict = json.load(f)


with open(root / f"json/{repo_name}.json") as f:
    cmd_dict = json.load(f)


runner = CliRunner()
result = runner.invoke(cli.main, repo_opt + cmd_dict["bind"])
print(result.exit_code)
