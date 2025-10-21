import json
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import sympy as sy
from PIL import Image
from scipy import signal
from sklearn.metrics import r2_score

from . import fast, latex, readme, utils
from .makefile import makefile
from .naive import naive_convolve


def package_clib():
    return Path(__file__).resolve().parent / "clib"


def read_init(repo):
    with open(repo.file_init) as f:
        data = json.load(f)
    c = data["c"]
    a = data["a"]
    b = data["b"]
    dim = data["dim"]
    return dim, c, b, a


def read_build_1d(repo):
    with open(repo.file_build) as f:
        data = json.load(f)
    p = data["p"]
    c = sy.Matrix(data["c"])
    b = sy.Matrix(data["b"])
    a = sy.Matrix(data["a"])
    q = sy.Matrix([sy.Rational(p, q) for p, q in data["q"]])
    return p, c, b, a, q


def read_build_2d(repo):
    with open(repo.file_build) as f:
        data = json.load(f)
    p = sy.Matrix(data["p"][0]), sy.Matrix(data["p"][1])
    c = sy.Matrix(data["c"][0]), sy.Matrix(data["c"][1])
    b = sy.Matrix(data["b"][0]), sy.Matrix(data["b"][1])
    a = sy.Matrix(data["a"][0]), sy.Matrix(data["a"][1])
    q = [sy.Matrix([sy.Rational(p, q) for p, q in d]) for d in data["q"]]
    return p, c, b, a, q


def read_init_if_exists(repo):
    if repo.file_init.exists() is False:
        return {}
    with open(repo.file_init) as f:
        data = json.load(f)
    return data


def read_num_points(repo):
    if repo.file_init.exists() is False:
        return 1
    dim, c, b, a = read_init(repo)
    return c


def num_points1d(size):
    if isinstance(size, int):
        return size
    else:
        return 1


def num_points2d(size, axis):
    if isinstance(size, list) is False:
        return 1
    return size[axis]


def default_toom_cook_points1d(size):
    if isinstance(size, int) is False:
        return 1
    p0 = [p * s for s in range(1, size // 2 + size % 2) for p in [1, -1]]
    p = [0] + p0[: size - 1 - size % 2] + ["inf"]
    return p


def default_toom_cook_points2d(size0, axis=None):
    if isinstance(size0, list) is False:
        return 1
    size = size0[axis]
    p0 = [p * s for s in range(1, size // 2 + size % 2) for p in [1, -1]]
    p = [0] + p0[: size - 1 - size % 2] + ["inf"]
    return p


def read_quant_if_exists(repo):
    if repo.file_quant.exists() is False:
        return {}
    with open(repo.file_quant) as f:
        data = json.load(f)
    return data


def now():
    return datetime.now().strftime("%Y%m%d-%H%M")


def write_bind(repo, func, params=None):
    data = {"func": func, "params": params}
    with open(repo.file_bind, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_bind_if_exists(repo):
    if repo.file_bind.exists() is False:
        return {}
    with open(repo.file_bind) as f:
        data = json.load(f)
    return data


def header_init(repo, dimensions, a, b, c, m):
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    init_path = repo.dir_clib_data / "init.h"
    dict_defs = dict_dimension(dimensions, a, b, c, m)
    utils.c_header(init_path, [], dict_defs)


def dict_dimension(dim, a, b, c, m):
    if dim == 1:
        dict_defs = {
            "A_SIZE": a,
            "B_SIZE": b,
            "C_SIZE": c,
            "M_SIZE": m,
        }
    else:
        dict_defs = {
            "A1_SIZE": a,
            "B1_SIZE": b,
            "C1_SIZE": c,
            "M1_SIZE": m,
            "A2_SIZE": a,
            "B2_SIZE": b,
            "C2_SIZE": c,
            "M2_SIZE": m,
        }
    return dict_defs


def cmd_init(repo, dimensions, in_len, out_len, w):
    if repo.file_init.exists():
        return "init.json existis, fconv model already initialized"
    # in_len = np.array(in_len)
    # w = np.array(w)
    # out_len = np.array(out_len)
    if in_len is None and out_len is None:
        b = in_len - out_len + 1
        c = in_len
        a = out_len
    elif in_len is None:
        c = out_len + w - 1
        a = out_len
        b = w
    elif out_len is None:
        a = in_len - w + 1
        c = in_len
        b = w
    else:
        return "Just one param is passed, inform another."

    if dimensions == 1:
        data = {
            "dim": dimensions,
            "c": c,
            "a": a,
            "b": b,
        }
    else:
        data = {
            "dim": dimensions,
            "c": [c] * dimensions,
            "a": [a] * dimensions,
            "b": [b] * dimensions,
        }

    repo.file_init.parent.mkdir(parents=True, exist_ok=True)
    with open(repo.file_init, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # # shutil.copytree(package_clib(), dir_clib, dirs_exist_ok=True)
    # shutil.copy(package_clib() / "Makefile", dir_clib / "Makefile")
    repo.dir_clib.mkdir(parents=True, exist_ok=True)
    dir_clib_x86 = repo.dir_clib / "cmake-gcc"
    shutil.copytree(
        package_clib() / "cmake-gcc", dir_clib_x86, dirs_exist_ok=True
    )
    dir_clib_common = repo.dir_clib / "common"
    shutil.copytree(
        package_clib() / "common", dir_clib_common, dirs_exist_ok=True
    )
    shutil.copytree(
        package_clib() / "src/int/lib", repo.dir_clib_lib, dirs_exist_ok=True
    )


def cmd_show(repo, init, build, quant_):
    init_data = read_init_if_exists(repo)
    if repo.file_init.exists():
        if init:
            return read_init_if_exists(repo)
        if build and repo.file_build.exists():
            if init_data["dim"] == 1:
                return read_build_1d(repo)
            elif init_data["dim"] == 2:
                return read_build_2d(repo)
        if quant_ and repo.file_quant.exists():
            return read_quant_if_exists(repo)


def cmd_build_toom_cook1d(repo, points):
    dim, c_len, b_len, a_len = read_init(repo)
    # at_len = ct_len + b_len - 1
    list_points = [np.inf if p == "inf" else int(p) for p in points]
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


def build1d(repo, list_points, a, b, c, q, b_len, c_len, readme_data):
    d = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len))))
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len))))
    # bg = fast.g_to_bg(q, b, g)
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
    # TODO export build_float.h with data in float
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
        package_clib() / "src/int/standard.c", repo.dir_clib_main / "standard.c"
    )
    shutil.copy(
        package_clib() / "src/int/filter1d.c", repo.dir_clib_main / "filter1d.c"
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
        '#ifndef C_OPTIM_H\n'
        '#define C_OPTIM_H\n\n'
        f"{matmul_a['header']}\n"
        f"{matmul_c['header']}\n"
        f"{hadamart['header']}\n"
        '#endif //C_OPTIM_H'
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
        "A_SIZE": a_len,
        "B_SIZE": b_len,
        "C_SIZE": c_len,
        "M_SIZE": len(q),
    }
    utils.sv_pkg(
        "pack_param", repo.dir_sv / "pack_param.sv", [], [], dict_param
    )


def cmd_build_toom_cook2d(repo, points1d, points2d):
    dim, c_len, b_len, a_len = read_init(repo)
    list_points1d = [np.inf if p == "inf" else int(p) for p in points1d]
    list_points2d = [np.inf if p == "inf" else int(p) for p in points2d]
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
    # at_len = ct_len + b_len - 1
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
    # bg1 = fast.g_to_bg(q1, b1, g1)
    qr1 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q1
    ]
    di2 = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len[1]))))
    g2 = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len[1]))))
    # bg2 = fast.g_to_bg(q2, b2, g2)
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
    # TODO export build_float.h with data in float
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
        "A1_SIZE": a_len[0],
        "B1_SIZE": b_len[0],
        "C1_SIZE": c_len[0],
        "M1_SIZE": len(q1),
        "A2_SIZE": a_len[0],
        "B2_SIZE": b_len[0],
        "C2_SIZE": c_len[0],
        "M2_SIZE": len(q1),
    }
    utils.sv_pkg(
        "pack_param", repo.dir_sv / "pack_param.sv", [], list_array, dict_param
    )


def cmd_build2d_bind_nest(repo):
    path = repo.dir_build / "bind-nest"
    path.mkdir(parents=True, exist_ok=True)
    # init_data = read_init(repo)
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

    # TODO export bind_kron_float.h with data in float
    csa_config = utils.csa_config_nest(a1, a2, c1, c2)
    utils.write_csa_config(csa_config, path / "csa")
    csa_parcels = utils.csa_parcels_nest(a1, a2, c1, c2)
    utils.write_csa_parcels(csa_parcels, path / "csa")

    dim, s_len, g_len, d_len = read_init(repo)
    c0_sv, c1_sv = utils.sv_nest(c1, s_len, "c")
    a1_sv, a0_sv = utils.sv_nest(a1, (q1.shape[0], q2.shape[0]), "a")
    repo.dir_sv.mkdir(exist_ok=True)
    with open(Path(__file__).parent / "template/nest.sv") as f:
        nest_sv = f.read()
    with open(repo.dir_sv / "mult_matrices.sv", "w") as f:
        str_sv = "\n\n\n".join([nest_sv, c0_sv, c1_sv, a1_sv, a0_sv])
        f.write(str_sv)

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
    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
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
        ["filter2d-nest", lib_opt, 3],
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
    write_bind(repo, "kron")

    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
    d1_user = sy.Matrix(
        c1.shape[0],
        c2.shape[0],
        sy.symbols(
            " ".join(f"d_{{{i}}}" for i in range(c1.shape[0] * c2.shape[0]))
        ),
    )
    g1_user = sy.Matrix(
        b1.shape[1],
        b2.shape[1],
        sy.symbols(
            " ".join(f"g_{{{i}}}" for i in range(b1.shape[1] * b2.shape[1]))
        ),
    )
    latex.latex_2d_bind_kron(
        build_data, d1_user, g1_user, path / "bind-kron", True
    )
    a = np.kron(a1, a2)
    c = np.kron(c1, c2)

    with open(repo.file_gen) as f:
        generator = json.load(f)

    gen_text = vars(readme)[generator["generator"]]
    a_sum = utils.count_sums(a)
    c_sum = utils.count_sums(c)
    text = (
        f"Total multiplications: {len(q1) * len(q2)}\n"
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
        f"{gen_text}\n"
        "## Bind\n"
        f"{readme.bind_kron}\n"
        "## Operations\n"
        f"{text}"
    )
    with open(repo.dir_clib / "README.md", "w") as f:
        f.write(readme_str)

    # TODO export bind_kron_float.h with data in float
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

    list_array = [
        {"name": "ma_kron", "value": a.T},
        {"name": "mc_kron", "value": c.T},
    ]
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


def cmd_quant_none(repo):
    repo.file_quant.unlink(missing_ok=True)


def cmd_quant_shift(repo, bits):
    data = {"bits": bits}
    with open(repo.file_quant, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def cmd_sim_file(repo, feature_info, weight, suffix, standard):
    dim, c_len, b_len, a_len = read_init(repo)
    quant_data = read_quant_if_exists(repo)
    with open(feature_info) as f:
        image = Image.open(feature_info)
    with open(weight) as f:
        w_arr = np.array(json.load(f))
    if dim == 1:
        wght_arr = w_arr.reshape(b_len, b_len)
    else:
        wght_arr = w_arr.reshape(b_len[0], b_len[1])
    if image.mode == "L":
        feat_arr = np.expand_dims(image, axis=(0, 1)).astype(int)
        wght_arr = np.expand_dims(wght_arr, axis=(0, 1))
    elif image.mode == "RGB":
        feat_arr = np.expand_dims(image, axis=0).astype(int)
        wght_arr = np.expand_dims(wght_arr, axis=0)
    image_side = feat_arr.shape[-1]
    if standard:
        return sim_default(
            a_len,
            b_len,
            c_len,
            dim,
            feat_arr,
            feature_info,
            image_side,
            quant_data,
            repo,
            suffix,
            weight,
            wght_arr,
        )
    else:
        return sim(
            a_len,
            b_len,
            c_len,
            dim,
            feat_arr,
            feature_info,
            image_side,
            quant_data,
            repo,
            suffix,
            weight,
            wght_arr,
            feat_arr.shape[1],
            1,
        )


def cmd_sim_int(
    repo,
    feature_info,
    weight,
    channel_in,
    channel_out,
    random,
    image_side,
    suffix,
    seed,
    standard,
):
    dim, c_len, b_len, a_len = read_init(repo)
    quant_data = read_quant_if_exists(repo)
    np.random.seed(seed)
    if random:
        feat_arr = np.random.randint(
            feature_info,
            feature_info + image_side,
            size=(1, channel_in, image_side, image_side),
        )
    else:
        feat = np.arange(
            feature_info,
            feature_info + channel_in * 1 * image_side**2,
        )
        feat_arr = feat.reshape(1, channel_in, image_side, image_side)
    w_len = b_len if dim == 1 else b_len[0]
    if random:
        wght_arr = np.random.randint(
            weight,
            weight + channel_out * channel_in * w_len**2,
            size=(channel_out, channel_in, w_len, w_len),
        )
    else:
        wght = np.arange(weight, weight + channel_out * channel_in * w_len**2)
        wght_arr = wght.reshape(channel_out, channel_in, w_len, w_len)

    if standard:
        return sim_default(
            a_len,
            b_len,
            c_len,
            dim,
            feat_arr,
            feature_info,
            image_side,
            quant_data,
            repo,
            suffix,
            weight,
            wght_arr,
        )
    else:
        return sim(
            a_len,
            b_len,
            c_len,
            dim,
            feat_arr,
            feature_info,
            image_side,
            quant_data,
            repo,
            suffix,
            weight,
            wght_arr,
            channel_in,
            channel_out,
        )


def cmd_sim_normal(
    repo, image_side, channel_in, channel_out, suffix, seed, standard
):
    dim, c_len, b_len, a_len = read_init(repo)
    quant_data = read_quant_if_exists(repo)
    # quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    np.random.seed(seed)
    feat_arr = np.random.normal(
        0, 1, size=(1, channel_in, image_side, image_side)
    )
    # feat_quant = (
    #     feat_arr if len(quant_data) == 0 else feat_arr * (2**quant_bits)
    # ).astype(int)

    w_len = b_len if dim == 1 else b_len[0]
    wght_arr = np.random.normal(
        0, 1, size=(channel_out, channel_in, w_len, w_len)
    )
    if standard:
        return sim_default(
            a_len,
            b_len,
            c_len,
            dim,
            feat_arr,
            None,
            image_side,
            quant_data,
            repo,
            suffix,
            None,
            wght_arr,
        )
    else:
        return sim(
            a_len,
            b_len,
            c_len,
            dim,
            feat_arr,
            None,
            image_side,
            quant_data,
            repo,
            suffix,
            None,
            wght_arr,
            channel_in,
            channel_out,
        )


def sim(
    a_len,
    b_len,
    c_len,
    dim,
    feat_arr,
    feature_info,
    image_side,
    quant_data,
    repo,
    suffix,
    weight,
    wght_arr,
    channel_in=1,
    channel_out=1,
):
    import torch
    from torch import nn
    from torch.nn import functional as F

    # output_default = signal.convolve2d(
    #     feat_arr, wght_arr[::-1, ::-1], mode="valid"
    # )
    output_default = F.conv2d(
        torch.tensor(feat_arr),
        torch.tensor(wght_arr),
        stride=1,
    )
    # output_default = np.squeeze(output_default.numpy())
    # output_naive = naive_convolve(feat_arr, wght_arr)
    # compare_naive = np.all(output_default == output_naive)
    # text_equal = f"Output default and naive are equals: {compare_naive}\n"
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    # output_default_quant = (
    #     output_default if len(quant_data) == 0 else output_default * (2**quant_bits)
    # )
    # output_default_quant = output_default
    # feat_quant = feat_arr
    feat_quant = (
        feat_arr if len(quant_data) == 0 else feat_arr * (2**quant_bits)
    ).astype(int)

    wght_quant = (
        wght_arr if len(quant_data) == 0 else wght_arr * (2**quant_bits)
    ).astype(int)

    output_default_quant = F.conv2d(
        torch.tensor(feat_quant),
        torch.tensor(wght_quant),
        stride=1,
    )
    output_shape = [output_default.shape[-1], output_default.shape[-2]]
    if dim == 1:
        points, c, b, a, q = read_build_1d(repo)
        bg = np.array(
            [
                [
                    [
                        fast.g_to_bg(q, b, wght_quant[cout][cin][i]).T
                        for i in range(b_len)
                    ]
                    for cin in range(channel_in)
                ]
                for cout in range(channel_out)
            ]
        )
        bg_quant = (
            bg
            if quant_data == 0
            else np.round(np.array(bg).astype(float)).astype(int)
        )
        fast_conv = [
            [
                [
                    fast.wrap_convolution(
                        c, bg_quant[cout][cin][i], a, quant_bits
                    )
                    for i in range(b_len)
                ]
                for cin in range(channel_in)
            ]
            for cout in range(channel_out)
        ]

        output_fast_ = [
            [
                [
                    fast.filter1d_slide2d(
                        fast_conv[cout][cin][i],
                        feat_quant[0][cin],
                        output_shape,
                        i,
                        c_len,
                        a_len,
                    )
                    for i in range(b_len)
                ]
                for cin in range(channel_in)
            ]
            for cout in range(channel_out)
        ]
        output_fast = np.sum(axis=(1, 2), a=output_fast_)
        feat_list_sv = [
            fast.sliding1d_window2d(
                feat_quant[0][cin],
                output_fast[0],
                output_shape,
                c_len,
                a_len,
                False,
            )
            for cin in range(channel_in)
        ]
        feat_list_sv = np.array(feat_list_sv)
        out_feat_list_sv = [
            fast.sliding1d_window2d(
                feat_quant[0][0],
                output_fast[cout],
                output_shape,
                c_len,
                a_len,
                True,
            )
            for cout in range(channel_out)
        ]
        out_feat_list_sv = np.array(out_feat_list_sv)

        count_nest = np.prod(out_feat_list_sv.shape[:-1])
        count_mult = int(count_nest * len(q) * b_len)
    else:
        points, c, b, a, q = read_build_2d(repo)
        bg = np.array(
            [
                [
                    fast.g_to_bg2d(
                        q[0], b[0], q[1], b[1], wght_quant[cout, cin]
                    )
                    for cin in range(channel_in)
                ]
                for cout in range(channel_out)
            ]
        )
        bg_quant = (
            bg
            if quant_data == 0
            else np.round(np.array(bg).astype(float)).astype(int)
        )
        fast_conv = [
            [
                fast.wrap_convolution2d(
                    c[0], c[1], bg_quant[cout][cin], a[0], a[1], quant_bits
                )
                for cin in range(channel_in)
            ]
            for cout in range(channel_out)
        ]

        output_fast_ = np.array(
            [
                [
                    fast.filter2d_slide2d(
                        fast_conv[cout][cin],
                        feat_quant[0][cin],
                        output_shape,
                        c_len,
                        a_len,
                    )
                    for cin in range(channel_in)
                ]
                for cout in range(channel_out)
            ]
        )
        output_fast = np.sum(output_fast_, axis=1)
        feat_list_sv = [
            fast.sliding2d_window2d(
                feat_quant[0][cin],
                output_fast[0],
                output_shape,
                c_len,
                a_len,
                False,
            )
            for cin in range(channel_in)
        ]
        feat_list_sv = np.array(feat_list_sv)
        out_feat_list_sv = [
            fast.sliding2d_window2d(
                feat_quant[0][0],
                output_fast[cout],
                output_shape,
                c_len,
                a_len,
                True,
            )
            for cout in range(channel_out)
        ]
        out_feat_list_sv = np.array(out_feat_list_sv)
        # feat_list_sv = ["\n".join(f.tolist()) for f in feat_list_sv0
        count_nest = np.prod(out_feat_list_sv.shape[:-1])
        count_mult = int(
            count_nest
            * np.prod(
                [np.prod(np.array(q[0]).shape), np.prod(np.array(q[1]).shape)]
            )
        )

    if len(quant_data) != 0:
        metric = r2_score(
            output_default.reshape(-1),
            np.array(output_fast).reshape(-1) / (2**quant_bits),
        )
        text_metric = f"R2: {metric}\n"
    else:
        metric = np.all(np.array(output_default) == np.array(output_fast))
        text_metric = f"Output default and fast are equals: {metric}\n"

    size = np.prod(output_default.shape)
    text = (
        f"Feature: {feature_info}\n"
        f"Weights: {weight}\n"
        f"Image side: {image_side}\n"
        f"Quantization bits: {quant_bits}\n"
        # f"{text_equal}\n"
        f"{text_metric}\n"
        "Totals\n"
        "Naive\n"
        f"Convolutions: {size}\n"
        f"Multiplications: {size * 9}\n"
        f"Additions: {size * 8}\n"
        "Fast\n"
        f"Convolutions: {count_nest}\n"
        f"Multiplications: {count_mult}\n"
    )
    if len(suffix) > 0:
        path = repo.dir_sim / f"sim-{suffix}"
    else:
        path = repo.dir_sim / "sim"
    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", "w") as f:
        f.write(text)
    for arr, name in zip(
        [feat_quant, wght_quant, output_fast, output_default_quant],
        ["d", "g", "s", "s_default_quant"],
    ):
        np.savetxt(
            path / f"{name}.txt",
            np.array(arr).reshape(-1, arr.shape[-1]),
            fmt="%d",
        )

    for arr, name in zip(
        [feat_arr, wght_arr, output_default],
        ["d_default", "g_default", "s_default"],
    ):
        np.savetxt(
            path / f"{name}.txt",
            np.array(arr).reshape(-1, arr.shape[-1]),
            fmt="%f",
        )

    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    list_quant = [
        {
            "name": "weight",
            "value": wght_quant.reshape(-1, wght_quant.shape[-1]),
        },
        {
            "name": "weight_gg",
            "value": bg_quant.reshape(-1, bg_quant.shape[-1]),
        },
        {
            "name": "feat_in_quant",
            "value": feat_quant.reshape(-1, feat_quant.shape[-1]),
        },
        {
            "name": "feat_out",
            "value": output_fast.reshape(-1, output_fast.shape[-1]),
        },
    ]
    list_float = [
        {
            "name": "weight",
            "value": wght_arr.reshape(-1, wght_arr.shape[-1]),
        },
        {"name": "weight_gg", "value": bg.reshape(-1, bg.shape[-1])},
        {"name": "feat_in", "value": feat_arr.reshape(-1, feat_arr.shape[-1])},
        {
            "name": "feat_out",
            "value": output_default.reshape(-1, output_default.shape[-1]),
        },
    ]
    dict_def = {
        "QUANT_BITS": quant_bits,
        "W_SIZE": wght_quant.shape[-1],
        "FIN_SIZE": feat_arr.shape[-1],
        "FOUT_SIZE": output_default.shape[-1],
    }
    # for path, typ in zip(["sim.h", "sim_float.h"], ["int", "float"]):
    arr = [{**r, "type": "int"} for r in list_quant]
    utils.c_header(repo.dir_clib_data / "sim.h", arr, dict_def)
    arr_float = [{**r, "type": "float"} for r in list_float]
    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    utils.c_header(
        repo.dir_clib_data_float / "sim_float.h", arr_float, dict_def
    )
    out_dict = {"quant": len(quant_data) > 0, "metric": metric, "text": text}

    weight_sv = bg_quant.reshape(-1, bg_quant.shape[-1] * bg_quant.shape[-2])
    feat_list_sv = feat_list_sv.reshape(-1, feat_list_sv.shape[-1])
    out_feat_list_sv = out_feat_list_sv.reshape(-1, out_feat_list_sv.shape[-1])
    output_fast_list_sv = output_fast.reshape(-1, output_fast.shape[-1])

    const_data_size = (
        1
        + weight_sv.reshape(-1).shape[0]
        + np.array(feat_quant).reshape(-1).shape[0]
    )
    const_data_sv = [[[0]], weight_sv.tolist(), np.array(feat_list_sv).tolist()]

    list_array = [
        {
            "name": f"const_weight[{weight_sv.shape[0]}][{weight_sv.shape[1]}]",
            "value": weight_sv,
        },
        {
            "name": f"const_feat_in[{feat_list_sv.shape[0]}][{feat_list_sv.shape[1]}]",
            "value": feat_list_sv,
        },
        {
            "name": f"const_feat_out_batch[{out_feat_list_sv.shape[0]}][{out_feat_list_sv.shape[1]}]",
            "value": out_feat_list_sv,
        },
        {
            "name": f"const_feat_out[{output_fast_list_sv.shape[0]}][{output_fast_list_sv.shape[1]}]",
            "value": output_fast_list_sv,
        },
    ]
    arr = [{**r, "type": "int"} for r in list_array]

    list1d = [
        {
            "name": f"const_data[{const_data_size}]",
            "value": const_data_sv,
            "type": "int",
        }
    ]
    dict_def = {
        "QUANT_BITS": quant_bits,
        "FIN1_SIZE": feat_list_sv.shape[0],
        "FIN2_SIZE": feat_list_sv.shape[1],
        "FOUT1_SIZE": out_feat_list_sv.shape[0],
        "FOUT2_SIZE": out_feat_list_sv.shape[1],
        "FEAT_INPUT_SIZE": feat_arr.shape[-1],
        "FEAT_OUTPUT_SIZE": output_fast.shape[-1],
        "N_WINDOW": output_fast.shape[-1] // (a_len if dim == 1 else a_len[0]),
        # **dict_dim,
    }
    utils.sv_pkg("pack_data", path / "pack_data.sv", list1d, arr, dict_def)
    return out_dict


def sim_default(
    a_len,
    b_len,
    c_len,
    dim,
    feat_arr,
    feature_info,
    image_side,
    quant_data,
    repo,
    suffix,
    weight,
    wght_arr,
):
    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode="valid"
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    text_equal = f"Output default and naive are equals: {compare_naive}\n"
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    wght_quant = (
        wght_arr
        if len(quant_data) == 0
        else np.left_shift(wght_arr, quant_bits)
    )

    output_quant = np.right_shift(
        naive_convolve(feat_arr, wght_quant), quant_bits
    )
    feat_list_sv, out_feat_list_sv = fast.sliding2d_window2d(
        feat_arr, output_quant, output_default.shape, c_len, a_len
    )
    if len(quant_data) != 0:
        metric = r2_score(output_default.reshape(-1), output_quant.reshape(-1))
        text_metric = f"R2: {metric}%\n"
    else:
        metric = np.all(output_default == output_quant)
        text_metric = f"Output default and fast are equals: {metric}\n"
    size = output_default.size
    text = (
        f"Feature: {feature_info}\n"
        f"Weights: {weight}\n"
        f"Image side: {image_side}\n"
        f"{text_equal}"
        f"{text_metric}"
        "Totals\n"
        "Naive\n"
        f"Convolutions: {size}\n"
        f"Multiplications: {size * 9}\n"
        f"Additions: {size * 8}\n"
    )
    if len(suffix) > 0:
        path = repo.dir_sim / f"sim-{suffix}"
    else:
        path = repo.dir_sim / "sim"
    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", "w") as f:
        f.write(text)
    for arr, name in zip(
        [feat_arr, wght_quant, output_default, output_quant],
        ["d", "g", "s_default", "s"],
    ):
        np.savetxt(path / f"{name}.txt", arr, fmt="%d")
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    list_array = [
        {"name": "weight", "value": wght_quant},
        # {"name": "weight_gg_quant", "value": bg_quant},
        {"name": "feat_in", "value": feat_arr},
        {"name": "gold", "value": output_default},
        {"name": "gold_quant", "value": output_quant},
    ]
    dict_def = {
        "QUANT_BITS": quant_bits,
        "W_SIZE": wght_quant.shape[0],
        "FIN_SIZE": feat_arr.shape[0],
        "FOUT_SIZE": output_default.shape[0],
    }
    # for path, typ in zip(["sim.h", "sim_float.h"], ["int", "float"]):
    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "sim.h", arr, dict_def)
    arr_float = [{**r, "type": "float"} for r in list_array]
    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    utils.c_header(
        repo.dir_clib_data_float / "sim_float.h", arr_float, dict_def
    )
    out_dict = {"quant": len(quant_data) > 0, "metric": metric, "text": text}
    weight_sv = np.array(wght_quant).reshape(1, -1)
    w_size = (len(weight_sv), len(weight_sv[0]))
    fin_size = (len(feat_list_sv), len(feat_list_sv[0]))
    fout_size = (len(out_feat_list_sv), len(out_feat_list_sv[0]))
    list_array = [
        {
            "name": f"const_weight[{w_size[0]}][{w_size[1]}]",
            "value": weight_sv,
        },
        {
            "name": f"const_feat_in[{fin_size[0]}][{fin_size[1]}]",
            "value": feat_list_sv,
        },
        {
            "name": f"const_feat_out[{fout_size[0]}][{fout_size[1]}]",
            "value": out_feat_list_sv,
        },
    ]
    arr = [{**r, "type": "int"} for r in list_array]
    dict_def = {
        "QUANT_BITS": quant_bits,
        "FIN1_SIZE": fin_size[0],
        "N_WINDOW": output_fast.shape[0] // (a_len if dim == 1 else a_len[0]),
        "FIN2_SIZE": fin_size[1],
        "FOUT1_SIZE": fout_size[0],
        "FOUT2_SIZE": fout_size[1],
        # **dict_dim,
    }
    if len(quant_data) != 0:
        utils.sv_pkg("pack_data", path / "pack_data.sv", [], arr, dict_def)
    return out_dict


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
