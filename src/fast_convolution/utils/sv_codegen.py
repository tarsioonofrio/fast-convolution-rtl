from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
import sympy as sy

from .bitmath import _recursive_log2
from .matrix import iterate_matrix_product

PACKAGE_TEMPLATE = """package {name};

  timeunit 1ns;
  timeprecision 1ps;

{code}
endpackage
"""

SV_ARRAY_TEMPLATE = "  const {type} {name} = '{{\n{value}\n  }};\n"
SV_DEF_TEMPLATE = "  localparam int {key} = {value};\n"


def _format_list1d(entries: Sequence[Dict[str, object]]) -> List[str]:
    blocks = []
    for entry in entries:
        typ = str(entry["type"])
        name = str(entry["name"])
        value = entry["value"]
        rows = []
        for block in value:
            block_lines = ",\n".join(
                "    " + ", ".join(map(str, row)) for row in block
            )
            rows.append(block_lines)
        value_str = ",\n\n".join(rows)
        blocks.append(SV_ARRAY_TEMPLATE.format(type=typ, name=name, value=value_str))
    return blocks


def _format_list2d(entries: Sequence[Dict[str, object]]) -> List[str]:
    blocks = []
    for entry in entries:
        typ = str(entry["type"])
        name = str(entry["name"])
        arr = np.array(entry["value"]).astype(typ)
        if arr.ndim == 1:
            value_str = "    " + ", ".join(map(str, arr.tolist()))
        else:
            value_str = ",\n".join(
                ["    '{" + ", ".join(map(str, row)) + "}" for row in arr.tolist()]
            )
        blocks.append(SV_ARRAY_TEMPLATE.format(type=typ, name=name, value=value_str))
    return blocks


def sv_pkg(
    name: str,
    path: Path,
    list1d: Sequence[Dict[str, object]],
    list2d: Sequence[Dict[str, object]],
    definitions: Dict[str, object],
) -> None:
    definition_block = "".join(
        SV_DEF_TEMPLATE.format(key=key, value=value)
        for key, value in definitions.items()
    )
    array_blocks = _format_list1d(list1d) + _format_list2d(list2d)
    code_parts = []
    if definition_block:
        code_parts.append(definition_block)
    if array_blocks:
        code_parts.extend(array_blocks)
    code = "".join(code_parts)
    package_str = PACKAGE_TEMPLATE.format(
        name=name, code=code.rstrip() + ("\n" if code else "")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(package_str)


def is_two_power(number: int) -> bool:
    return number > 0 and (number & (number - 1)) == 0


def matmul_sv(m1: np.ndarray, m2: np.ndarray):
    row1, col2 = m1.shape[0], m2.shape[1]
    out = [[] for _ in range(row1 * col2)]
    for r, c, d1, d2 in iterate_matrix_product(m1, m2):
        if isinstance(d1, str):
            if d2 != 0:
                out[r * col2 + c].append(d1)
        elif d1 != 0:
            out[r * col2 + c].append(d2)
    return out


def matmul_sv2(m1: np.ndarray, m2: np.ndarray):
    row1, col2 = m1.shape[0], m2.shape[1]
    out_terms = [[] for _ in range(row1 * col2)]
    out_weights = [[] for _ in range(row1 * col2)]
    for r, c, d1, d2 in iterate_matrix_product(m1, m2):
        if d2 != 0:
            out_terms[r * col2 + c].append(d1)
        if d1 != 0:
            out_weights[r * col2 + c].append(d2)
    return out_terms, out_weights


def sv_bitshift(port: str, power: int):
    return [
        port if shift == 0 else f"{port} <<< {shift}"
        for shift in _recursive_log2(power)
    ]


def _build_csa_section(prefix: str, ports, powers):
    signal_decl = (
        "  logic_vector "
        + ", ".join(f"s{prefix}{idx}" for idx in range(len(ports)))
        + ";"
    )

    assignments = []
    for idx, (terms, weights) in enumerate(zip(ports, powers)):
        weighted = [
            sv_bitshift(term, power) if abs(power) != 0 else [term]
            for term, power in zip(terms, weights)
        ]
        flattened = [value for cluster in weighted for value in cluster]
        if not flattened:
            continue
        if len(flattened) == 1:
            assignments.append(f"  assign s{prefix}{idx} = {flattened[0]};")
        else:
            args = ", ".join(flattened)
            assignments.append(f"  CSA_{len(flattened)} csa_{prefix}{idx}({args}, s{prefix}{idx});")
    return signal_decl, assignments


def _build_output_assignments(prefix_p: str, prefix_n: str, ports_p, ports_n):
    lines = []
    for idx, (neg_terms, pos_terms) in enumerate(zip(ports_n, ports_p)):
        if pos_terms and neg_terms:
            lines.append(f"  assign soma[{idx}] = s{prefix_p}{idx} - s{prefix_n}{idx};")
        elif pos_terms:
            lines.append(f"  assign soma[{idx}] = s{prefix_p}{idx};")
        elif neg_terms:
            lines.append(f"  assign soma[{idx}] = s{prefix_n}{idx};")
    return lines


def _module_header(name: str, idx: int, type_in: str, type_out: str) -> List[str]:
    return [
        f"module Matrix{name.upper()}{idx}",
        "  import packConv::*;",
        "  (",
        f"    input  {type_in} P,",
        f"    output {type_out} soma",
        "  );",
        "  timeunit 1ns;",
        "  timeprecision 1ps;",
    ]


def sv_nest(matrix: sy.Matrix, input_shape: Tuple[int, int], name: str) -> Tuple[str, str]:
    matrix_idx = {"c": (0, 1), "a": (1, 0)}
    type_input = {
        "c": ("type_input", "type_matrix_c"),
        "a": ("type_weight", "type_matrix_a"),
    }
    type_output = {
        "c": ("type_matrix_c", "type_weight"),
        "a": ("type_matrix_a", "type_output"),
    }

    arr = np.array(matrix)
    arr_p = np.where(arr > 0, arr, 0)
    arr_n = np.where(arr < 0, arr, 0)

    modules = []
    for module_idx, (in_type, out_type) in enumerate(
        zip(type_input[name], type_output[name])
    ):
        header_lines = _module_header(name, matrix_idx[name][module_idx], in_type, out_type)
        if module_idx == 0:
            input_grid = np.array(
                [f"P[{i}]" for i in range(input_shape[0] * input_shape[1])]
            ).reshape(*input_shape)
            port_p, port_pp_raw = matmul_sv2(input_grid, arr_p)
            port_n, port_np_raw = matmul_sv2(input_grid, arr_n)
        else:
            input_grid = np.array(
                [f"P[{i}]" for i in range(input_shape[0] * matrix.shape[1])]
            ).reshape(input_shape[0], matrix.shape[1])
            port_pp_raw, port_p = matmul_sv2(arr_p.T, input_grid)
            port_np_raw, port_n = matmul_sv2(arr_n.T, input_grid)

        port_pp = [[p for p in powers if p != 0] for powers in port_pp_raw]
        port_np = [[p for p in powers if p != 0] for powers in port_np_raw]

        signal_p, assignments_p = _build_csa_section("p", port_p, port_pp)
        signal_n, assignments_n = _build_csa_section("n", port_n, port_np)
        outputs = _build_output_assignments("p", "n", port_p, port_n)

        module_str = "\n".join(
            header_lines
            + [signal_p, signal_n + "\n"]
            + assignments_p
            + assignments_n
            + outputs
            + ["endmodule"]
        )
        modules.append(module_str)
    return tuple(modules)


def sv_mux_mult(total: int, step: int) -> str:
    state_idx = [
        (state, list(range(start, min(start + step, total))))
        for state, start in enumerate(range(0, total, step))
    ]
    template_path = Path(__file__).resolve().parents[1] / "template/mux_mult.sv"
    with open(template_path) as fh:
        template = fh.read()

    case_lines = []
    for state, indices in state_idx:
        assignments = "".join(f"idx_out[{idx}]={value}; " for idx, value in enumerate(indices))
        selector = "default" if state == 0 else str(state)
        case_lines.append(f"      {selector}: begin {assignments}end")

    case_block = "\n".join(case_lines)
    return template.format(case=case_block, num_mult=step, state_mult=total // step)
