import numpy as np
import sympy as sy

from . import fast


def select_func(quant_data):
    mapping = {"shift": shift_func}
    func = mapping[quant_data["func"]]
    func_instance = func(**quant_data["params"])
    return func_instance


def select_conv1d(quant_data):
    mapping = {"shift": shift1d}
    func = mapping[quant_data["func"]]
    func_instance = func(**quant_data["params"])
    return func_instance


def select_conv2d(quant_data):
    mapping = {"shift": shift2d}
    func = mapping[quant_data["func"]]
    func_instance = func(**quant_data["params"])
    return func_instance


def shift_quant(g, bits):
    return g * (2**bits)


def shift_func(bits):
    def func(g):
        return shift_quant(g, bits)

    return func


# TODO maybe inject quant transform and inverse functions in fast.conv1d{2d}
# functions
def shift1d(bits):
    def conv1d(g, c, q, b, a):
        g0 = shift_quant(g, bits).tolist()
        bg0 = fast.g_to_bg(q, b, g0)
        bg = sy.Matrix(np.array(bg0, dtype=int))
        conv = fast.wrap_convolution(c, bg, a)

        def quant_conv(f):
            # fq = np.left_shift(f, bits)
            quant_out = conv(f)
            out = sy.Matrix(quant_out / (2**bits))
            return out

        return quant_conv

    return conv1d


def shift2d(bits):
    def conv2d(g, c1, q1, b1, a1, c2, q2, b2, a2):
        g0 = np.left_shift(g, bits).tolist()
        bg0 = fast.g_to_bg2d(q1, b1, q2, b2, g0)
        bg = sy.Matrix(np.array(bg0, dtype=int))
        conv = fast.wrap_convolution2d(c1, c2, bg, a1, a2)

        def quant_conv(f):
            # fq = np.left_shift(f, bits)
            quant_out = conv(f)
            out = sy.Matrix(quant_out / (2**bits))
            return out

        return quant_conv

    return conv2d
