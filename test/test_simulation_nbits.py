import numpy as np
import sympy as sy

from fast_convolution.fast import wrap_convolution
from fast_convolution.simulation import (
    _truncate_scaled_weight_transform,
    _weight_transform_scale_2d,
    _wrap_signed,
)
from fast_convolution.utils.sv_codegen import sv_pkg


def test_wrap_signed_uses_two_complement_width():
    values = np.array([127, 128, 255, -129], dtype=object)

    wrapped = _wrap_signed(values, 8)

    assert wrapped.tolist() == [127, -128, -1, 127]
    assert wrapped.dtype == np.int64


def test_wrap_signed_rejects_invalid_width():
    for nbits in (0, 64):
        try:
            _wrap_signed(np.array([0]), nbits)
        except ValueError as exc:
            assert "NBITS" in str(exc)
        else:
            raise AssertionError("invalid NBITS was accepted")


def test_fast_path_wraps_materialized_transform_and_mac_values():
    identity = sy.Matrix([[1]])
    convolution = wrap_convolution(
        identity, identity, identity, nbits=8
    )

    # The feature transform materializes 200 as signed 8-bit -56.  The MAC
    # result is then wrapped at the same width as the RTL product signal.
    assert int(convolution([200])[0]) == -56


def test_generated_sv_package_supports_nb_words(tmp_path):
    package_path = tmp_path / "pack_data.sv"
    sv_pkg(
        "pack_data",
        package_path,
        [],
        [
            {
                "name": "const_feat_in[2]",
                "type": "logic signed [15:0]",
                "value": np.array([[1, -2]], dtype=np.int64),
            }
        ],
        {"NBITS": 16, "QUANT_BITS": 8},
    )

    text = package_path.read_text()
    assert "localparam int NBITS = 16;" in text
    assert "const logic signed [15:0] const_feat_in[2]" in text
    assert "const int const_feat_in" not in text


def test_power_of_two_truncation_matches_signed_shift():
    values = np.array([15, -1, -9, 32], dtype=object)

    assert _truncate_scaled_weight_transform(values, 4, bits=20).tolist() == [3, -1, -3, 8]


def test_non_power_of_two_truncation_uses_floor_for_negative_values():
    values = np.array([71, -1, -35, -36, -37], dtype=object)

    assert _truncate_scaled_weight_transform(values, 36, bits=20).tolist() == [1, -1, -1, -1, -2]
    assert _truncate_scaled_weight_transform(values * 16, 576, bits=20).tolist() == [1, -1, -1, -1, -2]


def test_truncation_keeps_nbits_signed_wrap():
    values = np.array([127 * 4, -128 * 4, 255 * 4], dtype=object)

    assert _truncate_scaled_weight_transform(values, 4, bits=8).tolist() == [127, -128, -1]


def test_tcn_scales_are_accepted():
    q = [[sy.Rational(1, 6)], [sy.Rational(1, 6)]]

    assert _weight_transform_scale_2d(q) == 36
