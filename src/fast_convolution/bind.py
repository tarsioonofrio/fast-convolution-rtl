from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import sympy as sy

from . import latex, readme, utils
from .config import package_clib, read_build_2d, read_init, write_bind
from .makefile import makefile


def cmd_build2d_bind_nest(repo):
    path = repo.dir_build / "bind-nest"
    path.mkdir(parents=True, exist_ok=True)
    build_data = read_build_2d(repo)
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    write_bind(repo, "nest")
    with open(repo.file_gen) as f:
        generator = json.load(f)
    gen_text = vars(readme)[generator["generator"]]

    a1_sum = utils.count_sums(a1)
    a2_sum = utils.count_sums(a2)
    c1_sum = utils.count_sums(c1)
    c2_sum = utils.count_sums(c2)
    text = (
        f"Total multiplications: {len(q1) * len(q2)}\n"
        f"Sums:\n"
        f"A: {a1_sum + a2_sum}\n"
        f"C: {c1_sum + c2_sum}\n"
        f"Total: {a1_sum + a2_sum + c1_sum + c2_sum}\n"
    )
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)

    readme_str = (
        "# Fast Convolution\n"
        "## Generator\n"
        f"{gen_text}\n"
        "## Bind\n"
        f"{readme.bind_nested}\n"
        "## Operations\n"
        f"{text}"
    )
    with open(repo.dir_clib / "README.md", "w") as f:
        f.write(readme_str)

    csa_config = utils.csa_config_nest(a1, a2, c1, c2)
    utils.write_csa_config(csa_config, path / "csa")
    csa_parcels = utils.csa_parcels_nest(a1, a2, c1, c2)
    utils.write_csa_parcels(csa_parcels, path / "csa")

    dim, s_len, g_len, d_len = read_init(repo)
    c0_sv, c1_sv = utils.sv_nest(c1, s_len, "c")
    a1_sv, a0_sv = utils.sv_nest(a1, (q1.shape[0], q2.shape[0]), "a")
    c0_sv_direct, c1_sv_direct = utils.sv_nest_direct(c1, s_len, "c")
    a1_sv_direct, a0_sv_direct = utils.sv_nest_direct(
        a1, (q1.shape[0], q2.shape[0]), "a"
    )
    repo.dir_sv.mkdir(exist_ok=True)
    with open(Path(__file__).parent / "template/nest.sv") as f:
        nest_sv = f.read().rstrip()
    with open(repo.dir_sv / "mult_matrices_csa.sv", "w") as f:
        str_sv = "\n\n\n".join([nest_sv, c0_sv, c1_sv, a1_sv, a0_sv])
        f.write(str_sv + "\n")
    with open(repo.dir_sv / "mult_matrices.sv", "w") as f:
        str_sv = "\n\n\n".join(
            [nest_sv, c0_sv_direct, c1_sv_direct, a1_sv_direct, a0_sv_direct]
        )
        f.write(str_sv + "\n")

    total_mults = q1.shape[0] ** 2
    for steps in sy.divisors(total_mults):
        sv_mux_mult = utils.sv_mux_mult(total_mults, steps)
        with open(repo.dir_sv / f"mux_mult_{steps:02d}.sv", "w") as f:
            f.write(sv_mux_mult)

    d1_sym = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"d_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
        ),
    )
    g1_sym = sy.Matrix(
        b1.shape[1],
        b2.shape[1],
        sy.symbols(
            " ".join(f"g_{{{i}}}" for i in range(b1.shape[1] * b2.shape[1]))
        ),
    )
    latex.latex_2d_bind_nest(
        build_data, d1_sym, g1_sym, path / "bind-nest", True
    )

    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        package_clib() / "src/int/standard.c", repo.dir_clib_main / "standard.c"
    )
    shutil.copy(
        package_clib() / "src/int/filter2d-nest.c",
        repo.dir_clib_main / "filter2d-nest.c",
    )
    matmul_c2 = utils.c_matmul_shift_noloop_nest(
        c2, "c2", c2.T.shape, (c2.shape[0], q1.shape[0]), True
    )
    matmul_c1t = utils.c_matmul_shift_noloop_nest(
        c1.T, "c1t", (c1.shape[0], q1.shape[0]), (q2.shape[0], q1.shape[0])
    )
    hadamart = utils.c_hadamart_product_nollop(
        q1.shape[0] * q2.shape[0], "_nest"
    )
    matmul_a2 = utils.c_matmul_shift_noloop_nest(
        a2, "a2", (q1.shape[0], q2.shape[0]), (q1.shape[0], a2.shape[0]), True
    )
    matmul_a1t = utils.c_matmul_shift_noloop_nest(
        a1.T,
        "a1t",
        (q1.shape[0], a1.T.shape[0]),
        (a1.T.shape[0], a1.T.shape[0]),
    )

    c_fun = (
        '#include "optim.h"\n\n'
        f"{matmul_c2['function']}\n"
        f"{matmul_c1t['function']}\n"
        f"{hadamart['function']}\n"
        f"{matmul_a2['function']}\n"
        f"{matmul_a1t['function']}\n"
    )
    c_head = (
        '#ifndef C_OPTIM_H\n'
        '#define C_OPTIM_H\n\n'
        f"{matmul_c2['header']}\n"
        f"{matmul_c1t['header']}\n"
        f"{hadamart['header']}\n"
        f"{matmul_a2['header']}\n"
        f"{matmul_a1t['header']}\n"
        '#endif //C_OPTIM_H'
    )

    lib_opt = "filter2d-nest-opt"
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
        ["filter2d-nest", None, 0],
        ["filter2d-nest", lib_opt, 1],
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


def cmd_build2d_bind_kron(repo):
    path = repo.dir_build / "bind-kron"
    path.mkdir(parents=True, exist_ok=True)
    build_data = read_build_2d(repo)
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

    write_bind(repo, "kron")
    with open(repo.file_gen) as f:
        generator = json.load(f)
    gen_text = vars(readme)[generator["generator"]]

    a = utils.tensorprod(a1, a2)
    c = utils.tensorprod(c1, c2)
    q = utils.tensorprod(q1, q2)
    text = (
        f"Total multiplications: {q.shape[0]}\n"
        f"Sums:\n"
        f"A: {utils.count_sums(a)}\n"
        f"C: {utils.count_sums(c)}\n"
        f"Total: {utils.count_sums(a) + utils.count_sums(c)}\n"
    )
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)

    readme_str = (
        "# Fast Convolution\n"
        "## Generator\n"
        f"{gen_text}\n"
        "## Bind\n"
        f"{readme.bind_kron}\n"
        "## Operations\n"
        f"{text}"
    )
    with open(repo.dir_clib / "README.md", "w") as f:
        f.write(readme_str)

    csa_config = utils.csa_config(a, c)
    utils.write_csa_config(csa_config, path / "csa")
    csa_parcels = utils.csa_parcels(a, c)
    utils.write_csa_parcels(csa_parcels, path / "csa")

    list_array = [
        {"name": "ma_kron", "value": a.T},
        {"name": "mc_kron", "value": c.T},
    ]
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "build.h", arr, {})

    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "build_float.h", arr, {})

    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "bind_kron.h", arr, {})

    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "bind_kron_float.h", arr, {})

    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        package_clib() / "src/int/standard.c", repo.dir_clib_main / "standard.c"
    )
    shutil.copy(
        package_clib() / "src/int/filter2d-kron.c",
        repo.dir_clib_main / "filter2d-kron.c",
    )

    matmul_a = utils.c_matmul_shift_noloop(a.T, "a")
    matmul_c = utils.c_matmul_shift_noloop(c.T, "c")
    hadamart = utils.c_hadamart_product_nollop(a.shape[0])

    c_fun = (
        '#include "optim.h"\n\n'
        f"{matmul_a['function']}\n"
        f"{matmul_c['function']}\n"
        f"{hadamart['function']}\n"
    )
    c_head = (
        '#ifndef C_OPTIM_H\n'
        '#define C_OPTIM_H\n\n'
        f"{matmul_a['header']}\n"
        f"{matmul_c['header']}\n"
        f"{hadamart['header']}\n"
        '#endif //C_OPTIM_H'
    )

    lib_opt = "filter2d-kron-opt"
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
        ["filter2d-kron", None, 0],
        ["filter2d-kron", lib_opt, 1],
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
