from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from .bitmath import log2_lst
from .matrix import iterate_matrix_product

CArraySpec = Mapping[str, object]

HEADER_TEMPLATE = """#ifndef {guard}
#define {guard}

{code}
#endif //{guard}
"""

ARRAY_TEMPLATE = "const {type} {name}[{size}] = {{\n{value}\n}};\n"
DEF_TEMPLATE = "#define {key} {value}\n"


def _format_c_value(array: np.ndarray, value_type: str) -> str:
    formatted_rows: List[str] = []
    formatted = array.astype(value_type)
    rows = formatted.reshape((-1, formatted.shape[-1])) if formatted.ndim > 1 else formatted.reshape(1, -1)

    def format_scalar(value) -> str:
        if value_type == "float":
            return f"{float(value):g}f"
        return str(int(value)) if isinstance(value, (np.integer, int)) else str(value)

    for row in rows:
        formatted_rows.append("\t" + ", ".join(format_scalar(v) for v in row))
    return ",\n".join(formatted_rows)


def _format_c_array(entry: CArraySpec) -> str:
    value_type = str(entry["type"])
    name = str(entry["name"])
    value = np.array(entry["value"])
    shape = value.shape if value.shape else (1,)
    size = "*".join(map(str, shape)) or "1"
    value_str = _format_c_value(value, value_type)
    return ARRAY_TEMPLATE.format(type=value_type, name=name, size=size, value=value_str)


def c_header(path: Path, arrays: Sequence[CArraySpec], definitions: Mapping[str, object]) -> None:
    guard = f"C_{path.stem.upper()}_H"
    definitions_block = "".join(
        DEF_TEMPLATE.format(key=key, value=value) for key, value in definitions.items()
    )
    arrays_block = "".join(_format_c_array(array) for array in arrays)
    code = "\n".join(filter(None, [definitions_block, arrays_block]))
    content = HEADER_TEMPLATE.format(guard=guard, code=code.rstrip() + ("\n" if code else ""))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def c_shift(identifier: str, signal: int, shift: int) -> str:
    operator = "-" if signal < 0 else "+"
    if shift == 0:
        return f" {operator} {identifier}"
    return f" {operator} ({identifier} << {shift})"


def _collapse_shift_rows(rows: Sequence[List[List[str]]]) -> List[str]:
    collapsed = []
    for row in rows:
        collapsed.append("".join(segment for segment_group in row for segment in segment_group))
    return collapsed


def _format_function(name_suffix: str, body_lines: Sequence[str]) -> Dict[str, str]:
    header = f"void matrix_mul_shift_noloop_{name_suffix}(int *m_out, const int *m_in)"
    body = "\n".join(body_lines)
    function = f"{header}{{\n{body}\n}}\n"
    return {"header": f"{header};\n", "function": function}


def c_matmul_shift_noloop(matrix: np.ndarray, name_suffix: str) -> Dict[str, str]:
    matrix_log = log2_lst(matrix)
    var_in = [f"m_in[{idx}]" for idx in range(matrix.shape[1])]
    var_out = [f"m_out[{idx}]" for idx in range(matrix.shape[0])]

    shift_rows = [
        [
            [c_shift(var, entry["s"], exponent) for exponent in entry["z"]]
            for var, entry in zip(var_in, row)
            if "s" in entry and "z" in entry
        ]
        for row in matrix_log
    ]
    assignments = [
        f"\t{target} = {expression};"
        for target, expression in zip(var_out, _collapse_shift_rows(shift_rows))
    ]
    return _format_function(name_suffix, assignments)


def matmul(m1: np.ndarray, m2: np.ndarray):
    row1, col2 = m1.shape[0], m2.shape[1]
    out = [[] for _ in range(row1 * col2)]
    for r, c, d1, d2 in iterate_matrix_product(m1, m2):
        data = {d2: d1} if isinstance(d2, str) else {d1: d2}
        out[r * col2 + c].append(data)
    return out


def c_matmul_shift_noloop_nest(
    matrix: np.ndarray,
    name_suffix: str,
    input_shape: Tuple[int, int],
    output_shape: Tuple[int, int],
    swap: bool = False,
):
    matrix_log = log2_lst(matrix)
    input_vars = np.array([f"m_in[{i}]" for i in range(input_shape[0] * input_shape[1])]).reshape(*input_shape)
    mult_matrix = (
        matmul(input_vars, np.array(matrix_log)) if swap else matmul(np.array(matrix_log), input_vars)
    )
    var_out = [f"m_out[{idx}]" for idx in range(output_shape[0] * output_shape[1])]

    shift_rows = [
        [
            c_shift(identifier, entry["s"], exponent)
            for shift_entry in row_entries
            for identifier, entry in shift_entry.items()
            if "s" in entry and "z" in entry
            for exponent in entry["z"]
        ]
        for row_entries in mult_matrix
    ]
    assignments = [
        f"\t{target} = {''.join(row)};"
        for target, row in zip(var_out, shift_rows)
    ]
    return _format_function(name_suffix, assignments)


def c_hadamart_product_nollop(out_size: int, suffix: str = "") -> Dict[str, str]:
    lines = [f"\tout[{idx}] = in1[{idx}] * in2[{idx}];" for idx in range(out_size)]
    header = f"void hadamart_product_noloop{suffix}(int *out, const int *in1, const int *in2)"
    body = "\n".join(lines)
    function = f"{header}{{\n{body}\n}}\n"
    return {"header": f"{header};\n", "function": function}
