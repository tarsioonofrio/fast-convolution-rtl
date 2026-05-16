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
    (_, _), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data

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
    c0_sv, c1_sv = utils.sv_nest_csa_param(
        c1,
        s_len,
        "c",
        a1_size=d_len[0],
        c1_size=c1.shape[0],
        m1_size=q1.shape[0],
    )
    a1_sv, a0_sv = utils.sv_nest_csa_param(
        a1,
        (q1.shape[0], q2.shape[0]),
        "a",
        a1_size=d_len[0],
        c1_size=c1.shape[0],
        m1_size=q1.shape[0],
    )
    c0_sv_direct, c1_sv_direct = utils.sv_nest_direct(c1, s_len, "c")
    a1_sv_direct, a0_sv_direct = utils.sv_nest_direct(
        a1, (q1.shape[0], q2.shape[0]), "a"
    )
    repo.dir_sv.mkdir(exist_ok=True)
    with open(Path(__file__).parent / "template/nest.sv") as f:
        nest_sv = f.read().rstrip()
    with open(Path(__file__).parent / "template/nest_csa.sv") as f:
        nest_csa_sv = f.read().rstrip()
    with open(repo.dir_sv / "mult_matrices_csa.sv", "w") as f:
        str_sv = "\n\n".join(
            [
                nest_csa_sv.format(
                    a1_size=d_len[0],
                    c1_size=c1.shape[0],
                    m1_size=q1.shape[0],
                ),
                c0_sv,
                c1_sv,
                a1_sv,
                a0_sv,
            ]
        )
        while "\n\n\nmodule " in str_sv:
            str_sv = str_sv.replace("\n\n\nmodule ", "\n\nmodule ")
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
    (_, _), (c1, _), (_, _), (a1, _), (q1, q2) = build_data

    write_bind(repo, "kron")

    repo.dir_sv.mkdir(exist_ok=True)
    c_sv, a_sv = utils.sv_kron_modules(
        c1,
        a1,
        c_types=("type_input", "type_weight"),
        a_types=("type_weight", "type_output"),
        import_pkg="pack_typedef",
        names=("Transform", "Inverse"),
    )
    c_sv_direct, a_sv_direct = utils.sv_kron_modules_direct(
        c1,
        a1,
        c_types=("type_input", "type_weight"),
        a_types=("type_weight", "type_output"),
        import_pkg="pack_typedef",
        names=("Transform", "Inverse"),
    )
    with open(repo.dir_sv / "mult_matrices_csa.sv", "w") as f:
        f.write(f"{a_sv}\n\n\n{c_sv}\n")
    with open(repo.dir_sv / "mult_matrices.sv", "w") as f:
        f.write(f"{a_sv_direct}\n\n\n{c_sv_direct}\n")

    total_mults = q1.shape[0] * q2.shape[0]
    for steps in sy.divisors(total_mults):
        sv_mux_mult = utils.sv_mux_mult(total_mults, steps)
        with open(repo.dir_sv / f"mux_mult_{steps:02d}.sv", "w") as f:
            f.write(sv_mux_mult)
