import re
import shutil
from pathlib import Path

import pytest

from fast_convolution.repo import Repo
from fast_convolution.simulation import cmd_sim_normal

TEST_ROOT = Path(__file__).parent.resolve()


def _r2(text: str) -> float:
    match = re.search(r"R2: (-?[0-9.eE+-]+)", text)
    assert match, text
    return float(match.group(1))


@pytest.mark.parametrize("name", ["2d-ifn9", "2d-tcn9"])
def test_truncated_3x3_golden_is_a_correct_convolution(tmp_path, name):
    """The raw-weight contract must not inherit the legacy 3x3 weight-bank defect."""
    shutil.copytree(TEST_ROOT / name / "config", tmp_path / "config")

    output = cmd_sim_normal(
        Repo(str(tmp_path)),
        12,
        2,
        2,
        "trunc",
        0,
        None,
        False,
        export_c_headers=False,
        truncated_weight_transform=True,
    )

    assert _r2(output["text"]) > 0.99
