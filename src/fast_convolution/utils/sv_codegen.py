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


def _build_csa_section_param(prefix: str, ports, powers):
    signal_decl = (
        "  logic [NBITS-1:0] "
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
            assignments.append(
                f"  CSA_{len(flattened)} #(.NBITS(NBITS)) csa_{prefix}{idx}({args}, s{prefix}{idx});"
            )
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
        "  import pack_typedef::*;",
        "  (",
        f"    input  {type_in} P,",
        f"    output {type_out} soma",
        "  );",
        "  timeunit 1ns;",
        "  timeprecision 1ps;",
    ]


def _module_header_csa_param(
    name: str,
    idx: int,
    a1_size: int,
    c1_size: int,
    m1_size: int,
) -> List[str]:
    if name == "c" and idx == 0:
        params = [
            "    parameter int NBITS = 20,",
            f"    parameter int C1_SIZE = {c1_size},",
            f"    parameter int M1_SIZE = {m1_size}",
        ]
        ports = [
            "    input  logic [NBITS-1:0] P [C1_SIZE*C1_SIZE-1:0],",
            "    output logic [NBITS-1:0] soma [C1_SIZE*M1_SIZE-1:0]",
        ]
    elif name == "c" and idx == 1:
        params = [
            "    parameter int NBITS = 20,",
            f"    parameter int C1_SIZE = {c1_size},",
            f"    parameter int M1_SIZE = {m1_size}",
        ]
        ports = [
            "    input  logic [NBITS-1:0] P [C1_SIZE*M1_SIZE-1:0],",
            "    output logic [NBITS-1:0] soma [M1_SIZE*M1_SIZE-1:0]",
        ]
    elif name == "a" and idx == 1:
        params = [
            "    parameter int NBITS = 20,",
            f"    parameter int C1_SIZE = {c1_size},",
            f"    parameter int M1_SIZE = {m1_size}",
        ]
        ports = [
            "    input  logic [NBITS-1:0] P [M1_SIZE*M1_SIZE-1:0],",
            "    output logic [NBITS-1:0] soma [C1_SIZE*M1_SIZE-1:0]",
        ]
    else:
        params = [
            "    parameter int NBITS = 20,",
            f"    parameter int A1_SIZE = {a1_size},",
            f"    parameter int C1_SIZE = {c1_size},",
            f"    parameter int M1_SIZE = {m1_size}",
        ]
        ports = [
            "    input  logic [NBITS-1:0] P [C1_SIZE*M1_SIZE-1:0],",
            "    output logic [NBITS-1:0] soma [A1_SIZE*A1_SIZE-1:0]",
        ]

    return [
        f"module Matrix{name.upper()}{idx} #(",
        *params,
        "  ) (",
        *ports,
        "  );",
        "  timeunit 1ns;",
        "  timeprecision 1ps;",
    ]


def _module_header_named(
    name: str,
    type_in: str,
    type_out: str,
    import_pkg: str,
) -> List[str]:
    return [
        f"module {name}",
        f"  import {import_pkg}::*;",
        "  (",
        f"    input  {type_in} pin,",
        f"    output {type_out} pout",
        "  );",
        "  timeunit 1ns;",
        "  timeprecision 1ps;",
    ]


def _filter_terms_weights(terms, weights):
    filtered_terms = []
    filtered_weights = []
    for term_list, weight_list in zip(terms, weights):
        keep_weights = [weight for weight in weight_list if weight != 0]
        if len(keep_weights) != len(term_list):
            keep_weights = keep_weights[: len(term_list)]
        filtered_terms.append(term_list)
        filtered_weights.append(keep_weights)
    return filtered_terms, filtered_weights


def _format_weighted_sum(terms, weights) -> str:
    parts = []
    for term, weight in zip(terms, weights):
        if weight == 0:
            continue
        if weight == 1:
            parts.append(str(term))
        else:
            parts.append(f"({term} * {weight})")
    if not parts:
        return "0"
    return " + ".join(parts)


def _maybe_pad_term(term: str, pad: bool) -> str:
    if not pad:
        return term
    if not term.startswith("P[") or not term.endswith("]"):
        return term
    try:
        idx = int(term[2:-1])
    except ValueError:
        return term
    return f"P[{idx:02d}]"


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


def sv_nest_csa_param(
    matrix: sy.Matrix,
    input_shape: Tuple[int, int],
    name: str,
    a1_size: int,
    c1_size: int,
    m1_size: int,
) -> Tuple[str, str]:
    matrix_idx = {"c": (0, 1), "a": (1, 0)}

    arr = np.array(matrix)
    arr_p = np.where(arr > 0, arr, 0)
    arr_n = np.where(arr < 0, arr, 0)

    modules = []
    for module_idx, idx in enumerate(matrix_idx[name]):
        header_lines = _module_header_csa_param(
            name, idx, a1_size=a1_size, c1_size=c1_size, m1_size=m1_size
        )
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

        signal_p, assignments_p = _build_csa_section_param("p", port_p, port_pp)
        signal_n, assignments_n = _build_csa_section_param("n", port_n, port_np)
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


def sv_nest_direct(
    matrix: sy.Matrix,
    input_shape: Tuple[int, int],
    name: str,
) -> Tuple[str, str]:
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

        port_p, port_pp = _filter_terms_weights(port_p, port_pp_raw)
        port_n, port_np = _filter_terms_weights(port_n, port_np_raw)

        if module_idx == 0:
            output_rows = input_shape[0]
            output_cols = matrix.shape[1]
        else:
            output_rows = matrix.shape[1]
            output_cols = matrix.shape[1]

        assignments = []
        for idx, (p_terms, p_weights, n_terms, n_weights) in enumerate(
            zip(port_p, port_pp, port_n, port_np)
        ):
            pos_expr = _format_weighted_sum(p_terms, p_weights)
            neg_expr = _format_weighted_sum(
                n_terms,
                [abs(weight) for weight in n_weights],
            )
            if pos_expr != "0" and neg_expr != "0":
                expr = f"{pos_expr} - ({neg_expr})"
            elif pos_expr != "0":
                expr = pos_expr
            elif neg_expr != "0":
                expr = f"-({neg_expr})"
            else:
                expr = "0"
            assignments.append(
                {
                    "idx": idx,
                    "row": idx // output_cols,
                    "col": idx % output_cols,
                    "line": f"  assign soma[{idx}] = {expr};",
                }
            )

        assignments.sort(key=lambda entry: (entry["row"], entry["col"]))
        spaced_lines = [entry["line"] for entry in assignments]
        module_str = "\n".join(header_lines + [""] + spaced_lines + ["endmodule"])
        modules.append(module_str)
    return tuple(modules)


def sv_kron_modules(
    c_matrix: sy.Matrix,
    a_matrix: sy.Matrix,
    c_types: Tuple[str, str] = ("type_weight", "type_weight"),
    a_types: Tuple[str, str] = ("type_weight", "type_output"),
    import_pkg: str = "packConv",
    names: Tuple[str, str] = ("MatrixC", "MatrixA"),
) -> Tuple[str, str]:
    c_kron = np.kron(np.array(c_matrix), np.array(c_matrix)).T
    a_kron = np.kron(np.array(a_matrix), np.array(a_matrix)).T
    c_module = _sv_kron_module(
        names[0],
        c_kron,
        c_types[0],
        c_types[1],
        import_pkg,
    )
    a_module = _sv_kron_module(
        names[1],
        a_kron,
        a_types[0],
        a_types[1],
        import_pkg,
    )
    return c_module, a_module


def sv_kron_modules_direct(
    c_matrix: sy.Matrix,
    a_matrix: sy.Matrix,
    c_types: Tuple[str, str] = ("type_weight", "type_weight"),
    a_types: Tuple[str, str] = ("type_weight", "type_output"),
    import_pkg: str = "packConv",
    names: Tuple[str, str] = ("MatrixC", "MatrixA"),
) -> Tuple[str, str]:
    c_kron = np.kron(np.array(c_matrix), np.array(c_matrix)).T
    a_kron = np.kron(np.array(a_matrix), np.array(a_matrix)).T
    c_module = _sv_kron_module_direct(
        names[0],
        c_kron,
        c_types[0],
        c_types[1],
        import_pkg,
    )
    a_module = _sv_kron_module_direct(
        names[1],
        a_kron,
        a_types[0],
        a_types[1],
        import_pkg,
    )
    return c_module, a_module


def _sv_kron_module(
    name: str,
    matrix: np.ndarray,
    type_in: str,
    type_out: str,
    import_pkg: str,
) -> str:
    header_lines = _module_header_named(name, type_in, type_out, import_pkg)
    arr = np.array(matrix)
    pos_rows = []
    neg_rows = []
    has_neg = False
    for row in arr:
        pos_terms = []
        pos_weights = []
        neg_terms = []
        neg_weights = []
        for col, weight in enumerate(row):
            if weight == 0:
                continue
            term = f"pin[{col}]"
            if weight > 0:
                pos_terms.append(term)
                pos_weights.append(int(weight))
            else:
                neg_terms.append(term)
                neg_weights.append(int(weight))
                has_neg = True
        pos_rows.append((pos_terms, pos_weights))
        neg_rows.append((neg_terms, neg_weights))

    lines = []
    if has_neg:
        lines.append(f"  {type_out} cp, cn;")
        lines.append("")

    for idx, ((p_terms, p_weights), (n_terms, n_weights)) in enumerate(
        zip(pos_rows, neg_rows)
    ):
        pos_inputs = []
        for term, weight in zip(p_terms, p_weights):
            pos_inputs.extend(sv_bitshift(term, weight))
        neg_inputs = []
        for term, weight in zip(n_terms, n_weights):
            neg_inputs.extend(sv_bitshift(term, weight))

        if pos_inputs:
            dest = f"cp[{idx}]" if has_neg else f"pout[{idx}]"
            lines.append(
                f"  CSA_{len(pos_inputs)} sp{idx} ({', '.join(pos_inputs)},  {dest});"
            )
        if neg_inputs:
            dest = f"cn[{idx}]"
            lines.append(
                f"  CSA_{len(neg_inputs)} sn{idx} ({', '.join(neg_inputs)}, {dest} );"
            )
        if has_neg:
            if pos_inputs and neg_inputs:
                lines.append(f"  assign pout[{idx}] =  cp[{idx}] - cn[{idx}];")
            elif pos_inputs:
                lines.append(f"  assign pout[{idx}] =  cp[{idx}];")
            elif neg_inputs:
                lines.append(f"  assign pout[{idx}] = -cn[{idx}];")
            else:
                lines.append(f"  assign pout[{idx}] = 0;")
        lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    module_str = "\n".join(header_lines + [""] + lines + ["endmodule"])
    return module_str


def _sv_kron_module_direct(
    name: str,
    matrix: np.ndarray,
    type_in: str,
    type_out: str,
    import_pkg: str,
) -> str:
    header_lines = _module_header_named(name, type_in, type_out, import_pkg)
    arr = np.array(matrix)
    lines = []
    for idx, row in enumerate(arr):
        pos_terms = []
        pos_weights = []
        neg_terms = []
        neg_weights = []
        for col, weight in enumerate(row):
            if weight == 0:
                continue
            term = f"pin[{col}]"
            if weight > 0:
                pos_terms.append(term)
                pos_weights.append(int(weight))
            else:
                neg_terms.append(term)
                neg_weights.append(int(weight))

        pos_expr = _format_weighted_sum(pos_terms, pos_weights)
        neg_expr = _format_weighted_sum(
            neg_terms,
            [abs(weight) for weight in neg_weights],
        )
        if pos_expr != "0" and neg_expr != "0":
            expr = f"{pos_expr} - ({neg_expr})"
        elif pos_expr != "0":
            expr = pos_expr
        elif neg_expr != "0":
            expr = f"-({neg_expr})"
        else:
            expr = "0"
        lines.append(f"  assign pout[{idx}] = {expr};")

    module_str = "\n".join(header_lines + [""] + lines + ["endmodule"])
    return module_str


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
