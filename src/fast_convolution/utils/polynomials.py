from __future__ import annotations

from typing import Sequence

import numpy as np
import sympy as sy


def symmetrical_polynomial_factorization(
    polynomial: sy.Expr,
    di: Sequence[sy.Expr],
    gi: Sequence[sy.Expr],
) -> sy.Expr:
    """
    Remove the redundant middle term of a symmetrical polynomial (if present) and
    reconstruct the factorised expression aligned with the provided symbols.
    """
    terms = list(polynomial.args)
    quo, rem = divmod(len(terms), 2)

    if rem != 0 and (len(di) % 2 != 0 or len(gi) % 2 != 0):
        centre = (quo + rem) - 1
        filtered_terms = [term for idx, term in enumerate(terms) if idx != centre]
    else:
        filtered_terms = terms

    indices = [
        row_idx
        for row_idx, symbol in enumerate(di)
        for term in filtered_terms
        if term.coeff(symbol, 1) != 0
    ]

    products = [
        np.sum([component[i] for i in indices]) for component in (di, gi)
    ]
    prod_expr = np.prod(products)
    return prod_expr - (prod_expr.expand() - polynomial)
