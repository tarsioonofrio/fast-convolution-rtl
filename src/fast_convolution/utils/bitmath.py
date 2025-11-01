from __future__ import annotations

from typing import Dict, List, Sequence, Union

import numpy as np
import sympy as sy

MatrixLike = Union[
    sy.Matrix,
    np.ndarray,
    Sequence[Sequence[Union[int, sy.Expr]]],
]
Log2Entry = Dict[str, Union[int, List[int]]]


def _recursive_log2(value: int) -> List[int]:
    """Return the exponent positions of the set bits in ``value``."""
    value = abs(int(value))
    if value == 0:
        return []
    return [
        index for index, bit in enumerate(bin(value)[2:][::-1]) if bit == "1"
    ]


def recursive_log2(number: Union[int, sy.Integer, sy.Rational]) -> Log2Entry:
    """
    Decompose an integer or rational into powers-of-two metadata.
    """
    if number == 0:
        return {}

    sign = -1 if number < 0 else 1
    if isinstance(number, sy.Integer):
        return {"s": sign, "z": _recursive_log2(abs(int(number)))}

    if isinstance(number, sy.Rational):
        return {
            "s": sign,
            "p": _recursive_log2(abs(int(number.p))),
            "q": _recursive_log2(abs(int(number.q))),
        }

    return {"s": sign, "z": _recursive_log2(number)}


def log2_lst(matrix: MatrixLike) -> List[List[Log2Entry]]:
    arr = np.asarray(matrix)
    out: List[List[Log2Entry]] = [
        [recursive_log2(arr[r, c]) for c in range(arr.shape[1])]
        for r in range(arr.shape[0])
    ]
    return out


def log2_matrix(entries: List[List[Log2Entry]]) -> sy.Matrix:
    matrix = sy.zeros(len(entries), len(entries[0]))
    for row_index, row in enumerate(entries):
        for col_index, entry in enumerate(row):
            if "z" in entry:
                result = sum(
                    entry["s"]
                    * sy.UnevaluatedExpr(sy.Pow(2, z, evaluate=False))
                    for z in entry["z"]
                )
            elif "p" in entry:
                numerator = sum(
                    entry["s"]
                    * sy.UnevaluatedExpr(sy.Pow(2, pow_, evaluate=False))
                    for pow_ in entry["p"]
                )
                denominator_terms = entry["q"]
                if len(denominator_terms) == 1:
                    base = sy.UnevaluatedExpr(
                        sy.Pow(2, denominator_terms[0], evaluate=False)
                    )
                    denominator = sy.Pow(base, -1, evaluate=False)
                else:
                    denominator = denominator_terms
                result = numerator * denominator
            else:
                result = 0
            matrix[row_index, col_index] = result
    return matrix


def matrix_to_log2(matrix: MatrixLike) -> sy.Matrix:
    return log2_matrix(log2_lst(matrix))
