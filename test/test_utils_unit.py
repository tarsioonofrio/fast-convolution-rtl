from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import sympy as sy

from fast_convolution import utils


def test_recursive_log2_handles_int_and_rational():
    assert utils.recursive_log2(5) == {"s": 1, "z": [0, 2]}
    assert utils.recursive_log2(-5) == {"s": -1, "z": [0, 2]}

    rational = utils.recursive_log2(sy.Rational(3, 4))
    assert rational["s"] == 1
    assert rational["p"] == [0, 1]
    assert rational["q"] == [2]


def test_matrix_to_log2_roundtrips_values():
    matrix = sy.Matrix([[sy.Rational(3, 4), -sy.Integer(2)]])
    reconstructed = utils.matrix_to_log2(matrix)
    assert sy.simplify(reconstructed[0, 0] - sy.Rational(3, 4)) == 0
    assert sy.simplify(reconstructed[0, 1] + 2) == 0


def test_count_sums_matches_expected_operations():
    matrix = sy.Matrix([[1, -1], [2, 0]])
    assert utils.count_sums(matrix) == 3


def test_csa_config_and_parcels_structure(tmp_path: Path):
    a = sy.Matrix([[1, 0], [2, 1]])
    c = sy.Matrix([[1, -1], [0, 1]])

    config = utils.csa_config(a, c)
    assert config == {
        ("a", "p"): 1,
        ("a", "n"): 0,
        ("c", "p"): 0,
        ("c", "n"): 0,
    }

    parcels = utils.csa_parcels(a, c)
    assert set(parcels.keys()) == {("a", "p"), ("a", "n"), ("c", "p"), ("c", "n")}
    assert parcels[("a", "p")][0] == [[1, 0], [0, 1]]
    assert parcels[("a", "p")][1] == [[0, 1], [0, 0]]
    assert parcels[("c", "n")][0] == [[0, 0], [1, 0]]

    utils.write_csa_config(config, tmp_path / "config")
    cfg_text = (tmp_path / "config" / "config.txt").read_text().strip().splitlines()
    assert "1 a p" in cfg_text
    assert "0 c n" in cfg_text

    utils.write_csa_parcels(parcels, tmp_path / "parcels")
    info_lines = (tmp_path / "parcels" / "info.txt").read_text().strip().splitlines()
    assert any(line.endswith(" a p") for line in info_lines)
    assert (tmp_path / "parcels" / "ap.txt").exists()


def test_c_header_and_code_generation(tmp_path: Path):
    header_path = tmp_path / "example.h"
    arrays = [
        {"name": "values", "type": "int", "value": np.array([[1, 2], [3, 4]])},
    ]
    definitions = {"FOO": 42}
    utils.c_header(header_path, arrays, definitions)
    content = header_path.read_text()
    assert "#ifndef C_EXAMPLE_H" in content
    assert "#define FOO 42" in content
    assert "const int values[2*2]" in content

    mat = np.array([[1, -1]])
    fn = utils.c_matmul_shift_noloop(mat, "test")
    assert "matrix_mul_shift_noloop_test" in fn["header"]
    assert "m_out[0] =  + m_in[0] - m_in[1];" in fn["function"]

    fn_nested = utils.c_matmul_shift_noloop_nest(mat.reshape(1, 2), "nest", (2, 1), (1, 1))
    assert "matrix_mul_shift_noloop_nest" in fn_nested["function"]
    assert "m_out[0] =  + m_in[0] - m_in[1];" in fn_nested["function"]

    hadamart = utils.c_hadamart_product_nollop(3, "_suffix")
    assert "hadamart_product_noloop_suffix" in hadamart["header"]
    assert "out[2] = in1[2] * in2[2];" in hadamart["function"]

    assert utils.c_shift("x", 1, 0) == " + x"
    assert utils.c_shift("x", -1, 2) == " - (x << 2)"


def test_sv_helpers(tmp_path: Path):
    assert utils.is_two_power(8) is True
    assert utils.is_two_power(10) is False

    assert utils.sv_bitshift("p", 3) == ["p", "p <<< 1"]

    m1 = np.array([["a0", "a1"]])
    m2 = np.array([[1], [2]])
    assert utils.matmul_sv(m1, m2)[0] == ["a0", "a1"]
    ports, weights = utils.matmul_sv2(m1, m2)
    assert ports[0] == ["a0", "a1"]
    assert weights[0] == [1, 2]

    sv_pkg_path = tmp_path / "pack.sv"
    utils.sv_pkg(
        "pack_test",
        sv_pkg_path,
        [{"name": "data[2][2]", "type": "int", "value": [[[1, 2], [3, 4]]]}],
        [{"name": "matrix[2][2]", "type": "int", "value": [[1, 0], [0, 1]]}],
        {"CONST": 1},
    )
    pkg_text = sv_pkg_path.read_text()
    assert "package pack_test;" in pkg_text
    assert "localparam int CONST = 1;" in pkg_text
    assert "const int matrix[2][2]" in pkg_text

    modules = utils.sv_nest(sy.Matrix([[1, -1], [0, 1]]), (2, 2), "c")
    assert modules[0].startswith("module MatrixC0")
    assert "assign soma[1] = sp1 - sn1;" in modules[0]

    mux = utils.sv_mux_mult(4, 2)
    assert "case" in mux
    assert "default: begin" in mux
