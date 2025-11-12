import shutil

import pytest

from .conftest import file_list1d
from .lib import collect_repo_cases, list_cmd_common, load_common_commands, run

CASES_1D = collect_repo_cases(file_list1d)
CMD_COMMON = load_common_commands()


@pytest.mark.parametrize("case", CASES_1D, ids=lambda case: case.name)
def test_rm(case):
    shutil.rmtree(case.repo_path, ignore_errors=True)


@pytest.mark.parametrize("case", CASES_1D, ids=lambda case: case.name)
@pytest.mark.parametrize("cmd", ["init", "build"])
def test_project(case, cmd):
    run(cmd, case.repo_path, case.repo_opt, case.commands)


@pytest.mark.parametrize("case", CASES_1D, ids=lambda case: case.name)
@pytest.mark.parametrize("cmd", list_cmd_common)
def test_common(case, cmd):
    run(cmd, case.repo_path, case.repo_opt, CMD_COMMON)
