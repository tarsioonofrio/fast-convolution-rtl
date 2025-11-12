from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
import sympy as sy
from scipy import signal


def symmetrical_cyclic_convolution(x: Sequence[int], y: Sequence[int]) -> sy.Matrix:
    """
    Compute the cyclic convolution of two symmetrical sequences.
    """
    x_arr = np.asarray(x)
    size = x_arr.shape[0]
    xx = np.tile(x_arr.reshape(-1), 2)
    yy = np.asarray(y).reshape(-1)
    out = np.convolve(xx, yy)
    return sy.Matrix(out[size : 2 * size])


def winograd_cyclic_conv2x2(
    x: Sequence[sy.Expr], y: Sequence[sy.Expr]
) -> Tuple[sy.Expr, sy.Expr]:
    """
    Compute the Winograd minimal filtering 2x2 cyclic convolution.
    """
    ax0 = x[0] + x[1]
    ax1 = x[0] - x[1]
    bx0 = (y[0] + y[1]) / 2
    bx1 = (y[0] - y[1]) / 2

    m0 = ax0 * bx0
    m1 = ax1 * bx1
    return m0 + m1, m0 - m1


def conv_circ_fft(signal_arr: Sequence[float], kernel: Sequence[float]) -> np.ndarray:
    """
    Circular convolution via FFT for real-valued 1D sequences.
    """
    return np.real(
        np.fft.ifft(np.fft.fft(signal_arr) * np.fft.fft(kernel))
    )


def default_convolve(f: np.ndarray, w: np.ndarray) -> np.ndarray:
    """
    Mirror the kernel and convolve using scipy's default behaviour.
    """
    return signal.convolve(f, w[::-1, ::-1], mode="valid")
