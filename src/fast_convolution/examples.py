from __future__ import annotations

import numpy as np
import sympy as sy

from . import fast, latex, utils
from .config import (
    read_bind_if_exists,
    read_build_1d,
    read_build_2d,
    read_init,
    read_quant_if_exists,
)


def cmd_example_random(repo, feature, weight, suffix, quant):
    dim, c_len, b_len, a_len = read_init(repo)
    repo.dir_example.mkdir(parents=True, exist_ok=True)

    if len(suffix) > 0:
        path = repo.dir_example / f"example-random-{suffix}"
    else:
        path = repo.dir_example / "example-random"

    if dim == 1:
        f = np.random.randint(feature[0], feature[1], size=c_len)
        w = np.random.randint(weight[0], weight[1], size=b_len)
    else:
        f0 = np.random.randint(feature[0], feature[1], size=c_len[0] * c_len[1])
        f = np.array(f0).reshape(c_len[0], c_len[1])
        w0 = np.random.randint(weight[0], weight[1], size=b_len[0] * b_len[1])
        w = np.array(w0).reshape(b_len[0], b_len[1])
    example(dim, f, path, repo, w, quant)


def cmd_example_sequential(repo, feature, weight, suffix, quant):
    dim, c_len, b_len, a_len = read_init(repo)
    repo.dir_example.mkdir(parents=True, exist_ok=True)
    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    if len(suffix) > 0:
        path = repo.dir_example / f"example-seq-{suffix}"
    else:
        path = repo.dir_example / "example-seq"

    if dim == 1:
        f = np.arange(feature, feature + c_len)
        w = np.arange(weight, weight + b_len)
    else:
        f0 = np.arange(feature, feature + c_len[0] * c_len[1])
        f = np.array(f0).reshape(c_len[0], c_len[1])
        w0 = np.arange(weight, weight + b_len[0] * b_len[1])
        w = np.array(w0).reshape(b_len[0], b_len[1])
    example(dim, f, path, repo, w, quant)


def cmd_example_list(repo, feature, weight, suffix, quant):
    dim, c_len, b_len, a_len = read_init(repo)
    repo.dir_example.mkdir(parents=True, exist_ok=True)
    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    if len(suffix) > 0:
        path = repo.dir_example / f"example-list-{suffix}"
    else:
        path = repo.dir_example / "example-list"

    if dim == 1:
        if len(feature) != c_len:
            raise ValueError("feature length must match c_len")
        f = np.array(feature)
        if len(weight) != c_len:
            raise ValueError("weight length must match c_len")
        w = np.array(weight)
    else:
        if len(feature) != c_len[0] ** 2:
            raise ValueError("feature length must match c_len")
        f = np.array(feature).reshape(c_len[0], c_len[1])
        if len(weight) != b_len[0] ** 2:
            raise ValueError("weight length must match c_len")
        w = np.array(weight).reshape(b_len[0], b_len[1])
    example(dim, f, path, repo, w, quant)


def example(dim, f, path, repo, w, quant):
    quant_data = read_quant_if_exists(repo)
    quant_bits = (
        quant_data["bits"] if "bits" in quant_data and quant is True else 0
    )

    if dim == 1:
        d = sy.Matrix(f)
        g = sy.Matrix(w)
        s = utils.default_convolve(d, g)
        points, c, b, a, q = read_build_1d(repo)
        latex.latex_1d(c, b, a, q, path, d, g, False, quant_bits)
        repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
        bg = fast.g_to_bg(q, b, g)
        list_array = [
            {"name": "md", "value": d},
            {"name": "mg", "value": g},
            {"name": "mgg", "value": bg},
            {"name": "ms_gold", "value": s},
        ]
        arr = [{**r, "type": "int"} for r in list_array]
        utils.c_header(repo.dir_clib_data / "example.h", arr, {})
        arr = [{**r, "type": "float"} for r in list_array]
        utils.c_header(repo.dir_clib_data_float / "example_float.h", arr, {})
    else:
        d = sy.Matrix(f)
        g = sy.Matrix(w)
        s = utils.default_convolve(d, g)

        data_bind = read_bind_if_exists(repo)
        build_data = read_build_2d(repo)
        if data_bind["func"] == "nest":
            latex.latex_2d_bind_nest(build_data, d, g, path, False, quant_bits)
        if data_bind["func"] == "kron":
            latex.latex_2d_bind_kron(build_data, d, g, path, False, quant_bits)

        (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
        bg = fast.g_to_bg2d(q1, b1, q2, b2, g)
        repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
        list_array = [
            {"name": "md", "value": d},
            {"name": "mg", "value": g},
            {"name": "mgg", "value": bg},
            {"name": "ms_gold", "value": s},
        ]
        arr = [{**r, "type": "int"} for r in list_array]
        utils.c_header(repo.dir_clib_data / "example.h", arr, {})

        arr_float = [{**r, "type": "float"} for r in list_array]
        utils.c_header(
            repo.dir_clib_data_float / "example_float.h", arr_float, {}
        )
