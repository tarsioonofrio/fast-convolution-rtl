from __future__ import annotations

from typing import Generator, Tuple

import numpy as np


def iterate_matrix_product(m1: np.ndarray, m2: np.ndarray) -> Generator[Tuple[int, int, object, object], None, None]:
    """
    Yield the multiplicand pairs (d1, d2) for each entry of the matrix product m1 @ m2.
    """
    row1 = m1.shape[0]
    col2 = m2.shape[1]
    col2_row1 = m1.shape[1]
    in1 = m1.reshape(-1)
    in2 = m2.reshape(-1)
    for r in range(row1):
        for c in range(col2):
            for k in range(col2_row1):
                d1 = in1[r * col2_row1 + k]
                d2 = in2[k * col2 + c]
                yield r, c, d1, d2
