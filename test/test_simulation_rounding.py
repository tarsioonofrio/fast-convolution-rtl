import re
import shutil
from pathlib import Path

import numpy as np
import pytest

from fast_convolution.fast import _arithmetic_shift_matrix
from fast_convolution.repo import Repo
from fast_convolution.simulation import (
    _truncate_scaled_weight_transform,
    cmd_sim_normal,
)

TEST_ROOT = Path(__file__).parent.resolve()


def _r2(text: str) -> float:
    match = re.search(r"R2: (-?[0-9.eE+-]+)", text)
    assert match, text
    return float(match.group(1))


@pytest.mark.parametrize(
    ("shift", "expected_floor", "expected_nearest"),
    [
        (1, [-3, -2, -2, 1, 2, 2], [-2, -2, -1, 2, 2, 3]),
        (2, [-2, -1, -1, 0, 1, 1], [-1, -1, -1, 1, 1, 1]),
    ],
)
def test_arithmetic_shift_matrix_rounding_modes(
    shift, expected_floor, expected_nearest
):
    values = [-5, -4, -3, 3, 4, 5]

    floor = _arithmetic_shift_matrix(values, shift, rounding="floor")
    nearest = _arithmetic_shift_matrix(values, shift, rounding="nearest")

    assert [int(value) for value in floor] == expected_floor
    assert [int(value) for value in nearest] == expected_nearest


def test_arithmetic_shift_matrix_zero_shift_ignores_rounding():
    values = [-5, -4, -3, 3, 4, 5]

    for rounding in ("floor", "nearest"):
        shifted = _arithmetic_shift_matrix(values, 0, rounding=rounding)
        assert [int(value) for value in shifted] == values


def test_arithmetic_shift_matrix_rejects_unknown_rounding():
    with pytest.raises(ValueError, match="rounding"):
        _arithmetic_shift_matrix([1], 1, rounding="ceil")


def test_truncate_scaled_weight_transform_scale_36():
    values = np.array([71, -1, -35, -36, -37], dtype=object)

    floor = _truncate_scaled_weight_transform(
        values, 36, bits=20, rounding="floor"
    )
    nearest = _truncate_scaled_weight_transform(
        values, 36, bits=20, rounding="nearest"
    )

    assert floor.tolist() == [1, -1, -1, -1, -2]
    assert nearest.tolist() == [2, 0, -1, -1, -1]


def test_truncate_scaled_weight_transform_scale_64():
    values = np.array([95, -1, -33, 32, -32, 96], dtype=object)

    floor = _truncate_scaled_weight_transform(
        values, 64, bits=20, rounding="floor"
    )
    nearest = _truncate_scaled_weight_transform(
        values, 64, bits=20, rounding="nearest"
    )

    assert floor.tolist() == [1, -1, -1, 0, -1, 1]
    assert nearest.tolist() == [1, 0, -1, 1, 0, 2]


def test_truncate_scaled_weight_transform_rejects_unknown_rounding():
    with pytest.raises(ValueError, match="rounding"):
        _truncate_scaled_weight_transform([1], 4, rounding="ceil")


def _simulate_truncated(repo, suffix, rounding=None):
    kwargs = {
        "export_c_headers": False,
        "truncated_weight_transform": True,
    }
    if rounding is not None:
        kwargs["weight_rounding"] = rounding
    output = cmd_sim_normal(
        repo,
        12,
        2,
        2,
        suffix,
        0,
        None,
        False,
        **kwargs,
    )
    return _r2(output["text"])


def test_truncated_weight_rounding_does_not_degrade_output(tmp_path):
    shutil.copytree(TEST_ROOT / "2d-tcn16" / "config", tmp_path / "config")
    repo = Repo(str(tmp_path))

    baseline = _simulate_truncated(repo, "round-default")
    floor = _simulate_truncated(repo, "round-floor", rounding="floor")
    nearest = _simulate_truncated(repo, "round-nearest", rounding="nearest")

    assert floor == pytest.approx(baseline)
    assert nearest >= floor
