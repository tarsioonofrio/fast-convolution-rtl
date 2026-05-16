from __future__ import annotations

import json
import shutil
from typing import Sequence

import numpy as np
import sympy as sy

from . import fast, latex, readme, utils
from .config import header_init, package_clib, read_init
from .makefile import makefile


def _to_numeric_points(points: Sequence[str]) -> list:
    return [np.inf if p == "inf" else int(p) for p in points]


def cmd_build_toom_cook1d(repo, points):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points = _to_numeric_points(points)
    c, q, b, a = fast.toom_cook(a_len, b_len, list_points)
    build1d(repo, list_points, a, b, c, q, b_len, c_len, readme.toom_cook)
    header_init(repo, dim, a_len, b_len, c_len, len(list_points))
    with open(repo.file_gen, "w", encoding="utf-8") as f:
        json.dump({"generator": "toom_cook"}, f, ensure_ascii=False, indent=4)


def cmd_build_manual_factorization1d(repo):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points = [1]
    c, q, b, a = fast.conv_manual_factorization()
    build1d(
        repo, list_points, a, b, c, q, b_len, c_len, readme.manual_factorization
    )
    header_init(repo, dim, a_len, b_len, c_len, 6)
    with open(repo.file_gen, "w", encoding="utf-8") as f:
        json.dump(
            {"generator": "manual_factorization"},
            f,
            ensure_ascii=False,
            indent=4,
        )


def cmd_build_tolimlin_4x3(repo):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points = [1]
    c, q, b, a = fast.conv_tolimlin_4x3()
    build1d(repo, list_points, a, b, c, q, b_len, c_len, readme.tolimlin_4x3)
    header_init(repo, dim, a_len, b_len, c_len, len(q))
    with open(repo.file_gen, "w", encoding="utf-8") as f:
        json.dump(
            {"generator": "tolimlin_4x3"},
            f,
            ensure_ascii=False,
            indent=4,
        )


def build1d(repo, list_points, a, b, c, q, b_len, c_len, readme_data):
    d = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len))))
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len))))
    qr = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q
    ]
    data = {
        "p": list_points,
        "c": np.array(c, dtype=int).tolist(),
        "q": qr,
        "b": np.array(b, dtype=int).tolist(),
        "a": np.array(a, dtype=int).tolist(),
    }
    with open(repo.file_build, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    repo.dir_build.mkdir(parents=True, exist_ok=True)
    path = repo.dir_build / "convolution"
    latex.latex_1d(c, b, a, sy.Matrix(q), path, d, g, True)
    a_sum = utils.count_sums(a)
    c_sum = utils.count_sums(c)
    text = (
        f"Total multiplications: {b_len}\n"
        f"Sums:\n"
        f"A: {a_sum}\n"
        f"C: {c_sum}\n"
        f"Total: {a_sum + c_sum}\n"
    )
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)

    readme_str = (
        "# Fast Convolution\n"
        "## Generator\n"
        f"{readme_data}\n"
        "## Operations\n"
        f"{text}"
    )
    with open(repo.dir_clib / "README.md", "w") as f:
        f.write(readme_str)

    csa_config = utils.csa_config(a, c)
    utils.write_csa_config(csa_config, path / "csa")
    csa_parcels = utils.csa_parcels(a, c)
    utils.write_csa_parcels(csa_parcels, path / "csa")
    header_csa = {
        f"{n.upper()}{s.upper()}_SIZE": p for (n, s), p in csa_config.items()
    }
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    csa_arr = [
        {
            "name": f"m{n}{s}",
            "value": np.array(lst).reshape(-1, len(lst[0][0])),
            "type": "int",
        }
        for (n, s), lst in csa_parcels.items()
    ]
    utils.c_header(repo.dir_clib_data / "build_shift.h", csa_arr, header_csa)
    list_array = [
        {"name": "mct", "value": c.T},
        {"name": "mb", "value": b},
        {"name": "mat", "value": a.T},
        {"name": "mq", "value": qr},
    ]
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "build.h", arr, {})
    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    arr_float = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "build_float.h", arr_float, {})
    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        package_clib() / "src/int/standard.c",
        repo.dir_clib_main / "standard.c",
    )
    shutil.copy(
        package_clib() / "src/int/filter1d.c",
        repo.dir_clib_main / "filter1d.c",
    )
    matmul_a = utils.c_matmul_shift_noloop(a.T, "a")
    matmul_c = utils.c_matmul_shift_noloop(c.T, "c")
    hadamart = utils.c_hadamart_product_nollop(c.T.shape[0])
    c_fun = (
        '#include "optim.h"\n\n'
        f"{matmul_a['function']}\n"
        f"{matmul_c['function']}\n"
        f"{hadamart['function']}\n"
    )
    c_head = (
        "#ifndef C_OPTIM_H\n"
        "#define C_OPTIM_H\n\n"
        f"{matmul_a['header']}\n"
        f"{matmul_c['header']}\n"
        f"{hadamart['header']}\n"
        "#endif //C_OPTIM_H"
    )
    lib_opt = "filter1d-opt"
    dir_lib_opt = repo.dir_clib_make / f"{lib_opt}/lib"
    dir_lib_opt.mkdir(parents=True, exist_ok=True)
    dir_lib_opt_inc = dir_lib_opt / "include"
    dir_lib_opt_inc.mkdir(parents=True, exist_ok=True)
    with open(dir_lib_opt / "optim.c", "w") as f:
        f.write(c_fun)
    with open(dir_lib_opt_inc / "optim.h", "w") as f:
        f.write(c_head)
    target_opt = [
        ["standard", None, 0],
        ["filter1d", None, 0],
        ["filter1d", lib_opt, 1],
    ]
    for target, name, opt in target_opt:
        source = "" if name is None else "$(CURDIR)/lib"
        include = "" if name is None else "$(CURDIR)/lib/include"
        makefile_str = makefile(target, opt, source, include)
        name_ = target if name is None else lib_opt
        dir_clib_make = repo.dir_clib_make / name_
        dir_clib_make.mkdir(parents=True, exist_ok=True)
        with open(dir_clib_make / "Makefile", "w") as f:
            f.write(makefile_str)
    repo.dir_sv.mkdir(parents=True, exist_ok=True)
    total_mults = q.shape[0]
    for steps in sy.divisors(total_mults):
        sv_mux_mult = utils.sv_mux_mult(total_mults, steps)
        with open(repo.dir_sv / f"mux_mult_{steps:02d}.sv", "w") as f:
            f.write(sv_mux_mult)
    dim, c_len, b_len, a_len = read_init(repo)

    dict_param = {
        "TRANSFORM_SIZE": a_len,
        "KERNEL_SIZE": b_len,
        "INVERSE_SIZE": c_len,
        "HADAMARD_SIZE": len(q),
    }
    utils.sv_pkg(
        "pack_param", repo.dir_sv / "pack_param.sv", [], [], dict_param
    )


def cmd_build_toom_cook2d(repo, points1d, points2d):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points1d = _to_numeric_points(points1d)
    list_points2d = _to_numeric_points(points2d)
    c1, q1, b1, a1 = fast.toom_cook(a_len[0], b_len[0], list_points1d)
    c2, q2, b2, a2 = fast.toom_cook(a_len[1], b_len[1], list_points2d)
    build2d(
        repo,
        list_points2d,
        list_points1d,
        a1,
        b1,
        c1,
        q1,
        a2,
        b2,
        c2,
        q2,
        b_len,
        c_len,
    )
    header_init(repo, dim, a_len[0], b_len[0], c_len[0], len(list_points1d))
    with open(repo.file_gen, "w", encoding="utf-8") as f:
        json.dump({"generator": "toom_cook"}, f, ensure_ascii=False, indent=4)


def cmd_build_manual_factorization2d(repo):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points1d = [1]
    list_points2d = [1]
    c1, q1, b1, a1 = fast.conv_manual_factorization()
    c2, q2, b2, a2 = fast.conv_manual_factorization()
    build2d(
        repo,
        list_points2d,
        list_points1d,
        a1,
        b1,
        c1,
        q1,
        a2,
        b2,
        c2,
        q2,
        b_len,
        c_len,
    )
    header_init(repo, dim, a_len[0], b_len[0], c_len[0], 6)
    with open(repo.file_gen, "w", encoding="utf-8") as f:
        json.dump(
            {"generator": "manual_factorization"},
            f,
            ensure_ascii=False,
            indent=4,
        )


def cmd_build_tolimlin_4x3_2d(repo):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points1d = [1]
    list_points2d = [1]
    c1, q1, b1, a1 = fast.conv_tolimlin_4x3()
    c2, q2, b2, a2 = fast.conv_tolimlin_4x3()
    build2d(
        repo,
        list_points2d,
        list_points1d,
        a1,
        b1,
        c1,
        q1,
        a2,
        b2,
        c2,
        q2,
        b_len,
        c_len,
    )
    header_init(repo, dim, a_len[0], b_len[0], c_len[0], len(q1))
    with open(repo.file_gen, "w", encoding="utf-8") as f:
        json.dump(
            {"generator": "tolimlin_4x3"},
            f,
            ensure_ascii=False,
            indent=4,
        )


def build2d(
    repo,
    list_points2d,
    list_points1d,
    a1,
    b1,
    c1,
    q1,
    a2,
    b2,
    c2,
    q2,
    b_len,
    c_len,
):
    di1 = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len[0]))))
    g1 = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len[0]))))
    qr1 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q1
    ]
    di2 = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len[1]))))
    g2 = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len[1]))))
    qr2 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q2
    ]
    data = {
        "p": [list_points1d, list_points2d],
        "c": [
            np.array(c1, dtype=int).tolist(),
            np.array(c2, dtype=int).tolist(),
        ],
        "q": [qr1, qr2],
        "b": [
            np.array(b1, dtype=int).tolist(),
            np.array(b2, dtype=int).tolist(),
        ],
        "a": [
            np.array(a1, dtype=int).tolist(),
            np.array(a2, dtype=int).tolist(),
        ],
    }
    with open(repo.file_build, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    repo.dir_build.mkdir(parents=True, exist_ok=True)
    path1 = repo.dir_build / "convolution-axis1"
    latex.latex_1d(c1, b1, a1, q1, path1, di1, g1, True)
    path2 = repo.dir_build / "convolution-axis2"
    latex.latex_1d(c2, b2, a2, q2, path2, di2, g2, True)
    list_array = [
        {"name": "mc1t", "value": c1.T},
        {"name": "mb1", "value": b1},
        {"name": "ma1t", "value": a1.T},
        {"name": "mq1", "value": qr1},
        {"name": "mc2t", "value": c2.T},
        {"name": "mb2", "value": b2},
        {"name": "ma2t", "value": a2.T},
        {"name": "mc2", "value": c2},
        {"name": "ma2", "value": a2},
        {"name": "mq2", "value": qr2},
    ]
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "build.h", arr, {})
    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    arr_float = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "build_float.h", arr_float, {})
    repo.dir_sv.mkdir(parents=True, exist_ok=True)
    dim, c_len, b_len, a_len = read_init(repo)
    c_index = (
        np.arange(c_len[0] * c_len[0]).reshape(c_len[0], c_len[0]).T.reshape(-1)
    )
    list_array = [
        {
            "name": f"c_index[{c_index.shape[0]}]",
            "value": c_index,
            "type": "int",
        },
    ]
    dict_param = {
        "TRANSFORM_SIZE": a_len[0],
        "KERNEL_SIZE": b_len[0],
        "INVERSE_SIZE": c_len[0],
        "HADAMARD_SIZE": len(q1),
    }
    utils.sv_pkg(
        "pack_param", repo.dir_sv / "pack_param.sv", [], list_array, dict_param
    )
