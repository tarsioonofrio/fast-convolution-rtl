import shutil
from pathlib import Path

import pytest

from .conftest import file_list1d
from .lib import read_json, run

# @pytest.fixture(scope="session")
# def file(pytestconfig):
#     return pytestconfig.getoption("file")


root = Path(__file__).parent.resolve()

# with open(root / "json/cmd_common.json") as f:
#     cmd_common_dict = json.load(f)

list_repo_path = [root / (Path(f).stem) for f in file_list1d]
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
