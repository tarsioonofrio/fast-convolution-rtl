import shutil
from pathlib import Path

import numpy as np
import pytest

from fast_convolution.config import read_init, read_quant_if_exists
from fast_convolution.repo import Repo
from fast_convolution.simulation import (
    SimulationPayload,
    _arithmetic_shift_array,
    _simulate_2d_core,
    _standard_convolve,
    _wrap_signed,
    cmd_sim_normal,
)

TEST_ROOT = Path(__file__).parent.resolve()


def _copy_config(name: str, tmp_path: Path) -> Repo:
    shutil.copytree(TEST_ROOT / name / "config", tmp_path / "config")
    shutil.copytree(TEST_ROOT / name / "build", tmp_path / "build")
    return Repo(str(tmp_path))


def _load_output(tmp_path: Path, suffix: str) -> np.ndarray:
    path = tmp_path / "sim" / f"sim-{suffix}" / "s.txt"
    return np.loadtxt(path, dtype=np.int64)


def test_zero_fractional_bits_matches_default(tmp_path):
    repo = _copy_config("2d-tcn16", tmp_path)

    cmd_sim_normal(
        repo,
        8,
        2,
        2,
        "frac-default",
        0,
        None,
        False,
        export_c_headers=False,
        truncated_weight_transform=True,
    )
    cmd_sim_normal(
        repo,
        8,
        2,
        2,
        "frac-zero",
        0,
        None,
        False,
        export_c_headers=False,
        truncated_weight_transform=True,
        weight_frac_bits=0,
        extra_frac_bits=0,
    )

    assert np.array_equal(
        _load_output(tmp_path, "frac-default"),
        _load_output(tmp_path, "frac-zero"),
    )


def test_fractional_bits_power_of_two_scale_matches_direct_convolution(
    tmp_path,
):
    repo = _copy_config("2d-tolimlin", tmp_path)
    dim, c_len, b_len, a_len = read_init(repo)
    quant_data = read_quant_if_exists(repo)
    quant_bits = quant_data["bits"]
    nbits = 40
    side = 5

    feature_int = np.arange(side**2).reshape(1, 1, side, side)
    weight_int = np.arange(1, 10).reshape(1, 1, 3, 3)
    feature_quant = _wrap_signed(feature_int << quant_bits, nbits)
    weight_quant = _wrap_signed(weight_int << quant_bits, nbits)

    payload = SimulationPayload(
        repo=repo,
        dim=dim,
        a_len=a_len,
        b_len=b_len,
        c_len=c_len,
        feature=feature_int.astype(float),
        feature_quant=feature_quant.copy(),
        feature_info=None,
        image_side=side,
        quant_data=quant_data,
        suffix="frac-direct",
        weight_info=None,
        weight=weight_int.astype(float),
        weight_quant=weight_quant.copy(),
        channel_in=1,
        channel_out=1,
        export_c_headers=False,
        truncated_weight_transform=True,
        weight_rounding="nearest",
        weight_frac_bits=2,
        extra_frac_bits=2,
        nbits=nbits,
    )

    core = _simulate_2d_core(
        payload,
        weight_quant,
        (side - 2, side - 2),
        quant_bits,
    )

    direct = _standard_convolve(feature_quant, weight_quant)
    expected = _arithmetic_shift_array(
        direct, quant_bits, rounding="nearest"
    )
    expected = _wrap_signed(expected, nbits)[0]

    assert np.array_equal(core.output_fast, expected)


def test_extra_fractional_bits_requires_truncated_transform(tmp_path):
    repo = _copy_config("2d-tcn16", tmp_path)

    with pytest.raises(ValueError, match="--truncated-weight-transform"):
        cmd_sim_normal(
            repo,
            8,
            1,
            1,
            "frac-invalid",
            0,
            None,
            False,
            export_c_headers=False,
            weight_frac_bits=1,
        )


def test_extra_fractional_bits_cannot_exceed_quant_plus_weight_bits(
    tmp_path,
):
    repo = _copy_config("2d-tcn16", tmp_path)

    with pytest.raises(ValueError, match="must not exceed"):
        cmd_sim_normal(
            repo,
            8,
            1,
            1,
            "frac-invalid",
            0,
            None,
            False,
            export_c_headers=False,
            truncated_weight_transform=True,
            weight_frac_bits=2,
            extra_frac_bits=11,
        )
