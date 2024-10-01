import json
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import sympy as sy
from PIL import Image
from scipy import signal
from sklearn.metrics import r2_score

from . import fast
from . import quant
from . import latex
from . import utils
from .naive import naive_convolve

from .makefile import makefile


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

    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    init_path = repo.dir_clib_data / "init.h"
    if dimensions == 1:
        dict_defs = {
            "A_SIZE": a,
            "B_SIZE": b,
            "C_SIZE": c,
        }
        utils.c_header(init_path, [], dict_defs)
    elif dimensions == 2:
        dict_defs = {
            "A1_SIZE": a,
            "B1_SIZE": b,
            "C1_SIZE": c,
            "A2_SIZE": a,
            "B2_SIZE": b,
            "C2_SIZE": c,
        }
        utils.c_header(init_path, [], dict_defs)

    # # shutil.copytree(package_clib(), dir_clib, dirs_exist_ok=True)
    # shutil.copy(package_clib() / "Makefile", dir_clib / "Makefile")
    repo.dir_clib.mkdir(parents=True, exist_ok=True)
    dir_clib_x86 = repo.dir_clib / "cmake-gcc"
    shutil.copytree(package_clib() / "cmake-gcc", dir_clib_x86, dirs_exist_ok=True)
    dir_clib_common = repo.dir_clib / "common"
    shutil.copytree(package_clib() / "common", dir_clib_common, dirs_exist_ok=True)
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
    d = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len))))
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len))))
    # bg = fast.g_to_bg(q, b, g)
    qr = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1] for i in q
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
    latex.build_1d(b, c, a, g, d, sy.Matrix(q), path)
    a_sum = fast.count_sums(a)
    c_sum = fast.count_sums(c)
    text = (
        f"Total multiplications: {b_len}\n"
        f"Sums:\n"
        f"A: {a_sum}\n"
        f"C: {c_sum}\n"
        f"Total: {a_sum + c_sum}\n"
    )
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)

    csa_config = fast.csa_config(a, c)
    fast.write_csa_config(csa_config, path / "csa")
    csa_parcels = fast.csa_parcels(a, c)
    fast.write_csa_parcels(csa_parcels, path / "csa")
    header_csa = {f"{n.upper()}{s.upper()}_SIZE": p for (n, s), p in csa_config.items()}

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
    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "build_float.h", arr, {})

    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    shutil.copy(package_clib() / "src/int/standard.c", repo.dir_clib_main / "standard.c")
    shutil.copy(package_clib() / "src/int/filter1d.c", repo.dir_clib_main / "filter1d.c")

    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    matmul_a = utils.c_matmul_shift_noloop(a.T, "a")
    matmul_c = utils.c_matmul_shift_noloop(c.T, "c")
    hadamart = utils.c_hadamart_product_nollop(len(list_points), c.T)

    dir_lib_opt_inc = repo.dir_clib_lib_opt / "include"
    dir_lib_opt_inc.mkdir(parents=True, exist_ok=True)
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
    with open(repo.dir_clib_lib_opt / "optim.c", "w") as f:
        f.write(c_fun)
    with open(dir_lib_opt_inc / "optim.h", "w") as f:
        f.write(c_head)

    for target, opt in [["standard", 0], ["filter1d", 0], ["filter1d", 1]]:
        source = ""  if opt == 0 else "$(SRCDIR)/lib_opt"
        include = ""  if opt == 0 else "$(SRCDIR)/lib_opt/include"
        makefile_str = makefile(target, opt, source, include)
        name = target if opt == 0 else f"{target}-opt"
        dir_clib_make = repo.dir_clib_make / name
        dir_clib_make.mkdir(parents=True, exist_ok=True)
        with open(dir_clib_make / "Makefile", "w") as f:
            f.write(makefile_str)


def cmd_build_toom_cook2d(repo, points1d, points2d):
    dim, c_len, b_len, a_len = read_init(repo)
    # at_len = ct_len + b_len - 1
    list_points1d = [np.inf if p == "inf" else int(p) for p in points1d]
    list_points2d = [np.inf if p == "inf" else int(p) for p in points2d]

    c1, q1, b1, a1 = fast.toom_cook(a_len[0], b_len[0], list_points1d)
    di1 = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len[0]))))
    g1 = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len[0]))))
    # bg1 = fast.g_to_bg(q1, b1, g1)
    qr1 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1] for i in q1
    ]

    c2, q2, b2, a2 = fast.toom_cook(a_len[1], b_len[1], list_points2d)
    di2 = sy.Matrix(sy.symbols(" ".join(f"d_{i}" for i in range(c_len[1]))))
    g2 = sy.Matrix(sy.symbols(" ".join(f"g_{i}" for i in range(b_len[1]))))
    # bg2 = fast.g_to_bg(q2, b2, g2)
    qr2 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1] for i in q2
    ]

    data = {
        "p": [list_points1d, list_points2d],
        "c": [np.array(c1, dtype=int).tolist(), np.array(c2, dtype=int).tolist()],
        "q": [qr1, qr2],
        "b": [np.array(b1, dtype=int).tolist(), np.array(b2, dtype=int).tolist()],
        "a": [np.array(a1, dtype=int).tolist(), np.array(a2, dtype=int).tolist()],
    }
    with open(repo.file_build, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    repo.dir_build.mkdir(parents=True, exist_ok=True)
    path1 = repo.dir_build / "convolution-axis1"
    latex.build_1d(b1, c1, a1, g1, di1, q1, path1)
    path2 = repo.dir_build / "convolution-axis2"
    latex.build_1d(b2, c2, a2, g2, di2, q2, path2)

    a1_sum = fast.count_sums(a1)
    a2_sum = fast.count_sums(a2)
    c1_sum = fast.count_sums(c1)
    c2_sum = fast.count_sums(c2)
    text = (
        f"Total multiplications: {b_len[0] * b_len[1]}\n"
        f"Sums:\n"
        f"A: {a1_sum + a2_sum}\n"
        f"C: {c1_sum + c2_sum}\n"
        f"Total: {a1_sum + a2_sum + c1_sum + c2_sum}\n"
    )
    path = repo.dir_build / "convolution-axis"
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)
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
    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "build_float.h", arr, {})


def cmd_build2d_bind_iterate(repo):
    path = repo.dir_build / "bind-iterated"
    path.mkdir(parents=True, exist_ok=True)
    init_data = read_init(repo)
    build_data = read_build_2d(repo)
    write_bind(repo, "iterate")
    latex.build_2d_bind_iterated(init_data, build_data, path)

    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    shutil.copy(package_clib() / "src/int/standard.c", repo.dir_clib_main / "standard.c")
    shutil.copy(package_clib() / "src/int/filter2d-iter.c", repo.dir_clib_main / "filter2d-iter.c")

    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
    matmul_c2 = utils.c_matmul_shift_noloop_iter(c2, "c2", c2.shape, c2.shape, True)
    matmul_c1t = utils.c_matmul_shift_noloop_iter(c1.T, "c1t", c1.T.shape, c1.T.shape)
    matmul_a2 = utils.c_matmul_shift_noloop_iter(a2, "a2", c1.shape, a2.shape, True)
    matmul_a1t = utils.c_matmul_shift_noloop_iter(
        a1.T, "a1t", a2.shape, (a1.T.shape[0], a1.T.shape[0])
    )
    hadamart = utils.c_hadamart_product_nollop(
        a1.shape[0] * a2.shape[0], np.kron(c1, c2), "_iter"
    )

    dir_lib_opt_inc = repo.dir_clib_lib_opt / "include"
    dir_lib_opt_inc.mkdir(parents=True, exist_ok=True)
    c_fun = (
        '#include "optim.h"\n\n'
        f"{matmul_c2['function']}\n"
        f"{matmul_c1t['function']}\n"
        f"{matmul_a2['function']}\n"
        f"{matmul_a1t['function']}\n"
        f"{hadamart['function']}\n"
    )
    c_head = (
        '#ifndef C_OPTIM_ITER_H\n'
        '#define C_OPTIM_ITER_H\n\n'
        f"{matmul_c2['header']}\n"
        f"{matmul_c1t['header']}\n"
        f"{matmul_a2['header']}\n"
        f"{matmul_a1t['header']}\n"
        f"{hadamart['header']}\n"
        '#endif //C_OPTIM_ITER_H'
    )
    with open(repo.dir_clib_lib_opt / "optim.c", "w") as f:
        f.write(c_fun)
    with open(dir_lib_opt_inc / "optim.h", "w") as f:
        f.write(c_head)

    for target, opt in [["standard", 0], ["filter2d-iter", 0], ["filter2d-iter", 1]]:
        source = ""  if opt == 0 else "$(SRCDIR)/lib_opt"
        include = ""  if opt == 0 else "$(SRCDIR)/lib_opt/include"
        makefile_str = makefile(target, opt, source, include)
        name = target if opt == 0 else f"{target}-opt"
        dir_clib_make = repo.dir_clib_make / name
        dir_clib_make.mkdir(parents=True, exist_ok=True)
        with open(dir_clib_make / "Makefile", "w") as f:
            f.write(makefile_str)

def cmd_build2d_bind_nest(repo):
    path = repo.dir_build / "bind-nest"
    path.mkdir(parents=True, exist_ok=True)
    init_data = read_init(repo)
    build_data = read_build_2d(repo)
    write_bind(repo, "nest")
    latex.build_2d_bind_nest(init_data, build_data, path)

    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
    a = np.kron(a1, a2)
    c = np.kron(c1, c2)

    # TODO export bind_nest_float.h with data in float
    csa_config = fast.csa_config(a, c)
    fast.write_csa_config(csa_config, path / "csa")
    csa_parcels = fast.csa_parcels(a, c)
    fast.write_csa_parcels(csa_parcels, path / "csa")

    list_array = [
        {"name": "ma_nest", "value": a.T},
        {"name": "mc_nest", "value": c.T},
    ]
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "build.h", arr, {})

    repo.dir_clib_data_float.mkdir(parents=True, exist_ok=True)
    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "build_float.h", arr, {})

    repo.dir_clib_main.mkdir(parents=True, exist_ok=True)
    shutil.copy(package_clib() / "src/int/standard.c", repo.dir_clib_main / "standard.c")
    shutil.copy(package_clib() / "src/int/filter2d-nest.c", repo.dir_clib_main / "filter2d-nest.c")

    matmul_a = utils.c_matmul_shift_noloop(a.T, "a")
    matmul_c = utils.c_matmul_shift_noloop(c.T, "c")
    hadamart = utils.c_hadamart_product_nollop(a.shape[0], c.T)

    dir_lib_opt_inc = repo.dir_clib_lib_opt / "include"
    dir_lib_opt_inc.mkdir(parents=True, exist_ok=True)
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
    with open(repo.dir_clib_lib_opt / "optim.c", "w") as f:
        f.write(c_fun)
    with open(dir_lib_opt_inc / "optim.h", "w") as f:
        f.write(c_head)

    for target, opt in [["standard", 0], ["filter2d-nest", 0], ["filter2d-nest", 1]]:
        source = ""  if opt == 0 else "$(SRCDIR)/lib_opt"
        include = ""  if opt == 0 else "$(SRCDIR)/lib_opt/include"
        makefile_str = makefile(target, opt, source, include)
        name = target if opt == 0 else f"{target}-opt"
        dir_clib_make = repo.dir_clib_make / name
        dir_clib_make.mkdir(parents=True, exist_ok=True)
        with open(dir_clib_make / "Makefile", "w") as f:
            f.write(makefile_str)



def cmd_quant_none(repo):
    repo.file_quant.unlink(missing_ok=True)


def cmd_quant_shift(repo, bits):
    data = {"func": "shift", "params": {"bits": bits}}
    with open(repo.file_quant, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def cmd_sim_file(repo, feature, weight, suffix):
    dim, c_len, b_len, a_len = read_init(repo)
    quant_data = read_quant_if_exists(repo)
    with open(feature) as f:
        image = Image.open(feature).convert("L")
        feat_arr = np.array(image)
    with open(weight) as f:
        w_arr = np.array(json.load(f))
        if dim == 1:
            wght_arr = w_arr.reshape(b_len, b_len)
        elif dim == 2:
            wght_arr = w_arr.reshape(b_len[0], b_len[1])

    output_default = signal.convolve2d(feat_arr, w_arr[::-1, ::-1], mode="valid")
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    text_equal = f"Output default and naive are equals: {compare_naive}\n"

    if dim == 1:
        points, c, b, a, q = read_build_1d(repo)
        # Corrected error in fast 1d conv
        # between C and python in quantized data
        # In python the data is right shifted and after that is summed
        # In C the data is summed and after that is summed
        # shift operator not is linear
        # i believe is better change C to be like the python code
        # data in right shifted and after that is summed
        # TODO
        # compose inverse quantization in filter like quant.select_conv2d

        bg = (
            np.array([fast.g_to_bg(q, b, wght_arr[i]) for i in range(b_len)])
            .reshape(b_len, -1)
            .tolist()
        )
        if len(quant_data) == 0:
            fast_conv = [fast.conv1d(wght_arr[i], c, q, b, a) for i in range(b_len)]
            output_fast = np.sum(
                axis=0,
                a=[
                    fast.filter1d_slide2d(
                        fast_conv[i], feat_arr, output_default.shape, i, c_len, a_len
                    )
                    for i in range(0, wght_arr.shape[0])
                ],
            )
            bg_quant = bg
        else:
            weight_quant = np.left_shift(wght_arr, quant_data["params"]["bits"])
            bg_q = [
                fast.g_to_bg(q, b, weight_quant[i])
                for i in range(0, weight_quant.shape[0])
            ]
            bg_quant_int = [
                sy.Matrix(np.array(bg_q[i], dtype=int))
                for i in range(0, weight_quant.shape[0])
            ]
            fast_conv = [
                fast.wrap_convolution(c, bg_quant_int[i], a)
                for i in range(0, weight_quant.shape[0])
            ]

            output_fast_ = np.sum(
                axis=0,
                a=[
                    fast.filter1d_slide2d(
                        fast_conv[i], feat_arr, output_default.shape, i, c_len, a_len
                    )
                    for i in range(0, wght_arr.shape[0])
                ],
            )
            output_fast = np.right_shift(output_fast_, quant_data["params"]["bits"])
            # wght_quant = quant.select_func(quant_data)(wght_arr)
            bg_quant = np.array(bg_q).reshape(b_len, -1).tolist()

        count_iter = fast.filter1d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points) * len(fast_conv)

    elif dim == 2:
        points, c, b, a, q = read_build_2d(repo)
        conv_func = (
            fast.conv2d if len(quant_data) == 0 else quant.select_conv2d(quant_data)
        )
        fast_conv = conv_func(wght_arr, c[0], q[0], b[0], a[0], c[1], q[1], b[1], a[1])
        output_fast = fast.filter2d_slide2d(
            fast_conv, feat_arr, output_default.shape, c_len, a_len
        )
        count_iter = fast.filter2d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points[0]) * len(points[1])
        bg = fast.g_to_bg2d(q[0], b[0], q[1], b[1], wght_arr)
        if len(quant_data) == 0:
            bg_quant = bg
        else:
            wght_quant = quant.select_func(quant_data)(wght_arr)
            bg_quant = fast.g_to_bg2d(q[0], b[0], q[1], b[1], wght_quant)

    if len(quant_data) != 0:
        metric = r2_score(output_default.reshape(-1), output_fast.reshape(-1))
        text_metric = f"R2: {metric}\n"
    else:
        metric = np.all(output_default == output_fast)
        text_metric = f"Output default and fast are equals: {metric}\n"

    size = output_default.size
    text = (
        f"Feature: {feature}\n"
        f"Weights: {weight}\n"
        f"{text_equal}"
        f"{text_metric}"
        "Totals\n"
        "Naive\n"
        f"Convolutions: {size}\n"
        f"Multiplications: {size * 9}\n"
        f"Additions: {size * 8}\n"
        "Fast\n"
        f"Convolutions: {count_iter}\n"
        f"Multiplications: {count_mult}\n"
    )
    if len(suffix) > 0:
        path = repo.dir_sim / f"file-{suffix}"
    else:
        path = repo.dir_sim / "file"

    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", "w") as f:
        f.write(text)

    for arr, name in zip(
        [feat_arr, wght_arr, output_default, output_fast], ["d", "g", "s_default", "s"]
    ):
        np.savetxt(path / f"{name}.txt", arr, fmt="%d")

    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    list_array = [
        {"name": "weight", "value": wght_arr},
        {"name": "weight_gg", "value": bg},
        {"name": "weight_gg_quant", "value": bg_quant},
        {"name": "feat_in", "value": feat_arr},
        {"name": "gold", "value": output_default},
        {"name": "gold_quant", "value": output_fast},
    ]
    quant_dict = (
        {f"QUANT_{k}".upper(): v for k, v in quant_data["params"].items()}
        if len(quant_data) > 0
        else {}
    )
    dict_def = {
        "QUANT": quant_data["func"].upper() if len(quant_data) > 0 else None,
        **quant_dict,
        "W_SIZE": wght_arr.shape[0],
        "FIN_SIZE": feat_arr.shape[0],
        "FOUT_SIZE": output_default.shape[0],
    }
    # for path, typ in zip(["sim.h", "sim_float.h"], ["int", "float"]):
    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "sim.h", arr, dict_def)

    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "sim_float.h", arr, dict_def)

    out_dict = {"quant": len(quant_data) > 0, "metric": metric, "text": text}
    return out_dict


def cmd_sim_random(repo, feature_random, weight_random, image_side, loop, suffix):
    dim, c_len, b_len, a_len = read_init(repo)
    quant_data = read_quant_if_exists(repo)
    feat = np.random.randint(feature_random[0], feature_random[1], size=image_side**2)
    feat_arr = feat.reshape(image_side, image_side)

    if dim == 1:
        wght = np.random.randint(weight_random[0], weight_random[1], size=b_len**2)
        wght_arr = wght.reshape(b_len, b_len)
    elif dim == 2:
        wght = np.random.randint(
            weight_random[0], weight_random[1], size=b_len[0] * b_len[1]
        )
        wght_arr = wght.reshape(b_len[0], b_len[1])

    output_default = signal.convolve2d(feat_arr, wght_arr[::-1, ::-1], mode="valid")
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    text_equal = f"Output default and naive are equals: {compare_naive}\n"

    if dim == 1:
        points, c, b, a, q = read_build_1d(repo)
        # Corrected error in fast 1d conv
        # between C and python in quantized data
        # In python the data is right shifted and after that is summed
        # In C the data is summed and after that is summed
        # shift operator not is linear
        # i believe is better change C to be like the python code
        # data in right shifted and after that is summed
        # TODO
        # compose inverse quantization in filter like quant.select_conv2d

        bg = (
            np.array([fast.g_to_bg(q, b, wght_arr[i]) for i in range(b_len)])
            .reshape(b_len, -1)
            .tolist()
        )
        if len(quant_data) == 0:
            fast_conv = [fast.conv1d(wght_arr[i], c, q, b, a) for i in range(b_len)]
            output_fast = np.sum(
                axis=0,
                a=[
                    fast.filter1d_slide2d(
                        fast_conv[i], feat_arr, output_default.shape, i, c_len, a_len
                    )
                    for i in range(0, wght_arr.shape[0])
                ],
            )
            bg_quant = bg
        else:
            weight_quant = np.left_shift(wght_arr, quant_data["params"]["bits"])
            bg_q = [
                fast.g_to_bg(q, b, weight_quant[i])
                for i in range(0, weight_quant.shape[0])
            ]
            bg_quant_int = [
                sy.Matrix(np.array(bg_q[i], dtype=int))
                for i in range(0, weight_quant.shape[0])
            ]
            fast_conv = [
                fast.wrap_convolution(c, bg_quant_int[i], a)
                for i in range(0, weight_quant.shape[0])
            ]

            output_fast_ = np.sum(
                axis=0,
                a=[
                    fast.filter1d_slide2d(
                        fast_conv[i], feat_arr, output_default.shape, i, c_len, a_len
                    )
                    for i in range(0, wght_arr.shape[0])
                ],
            )
            output_fast = np.right_shift(output_fast_, quant_data["params"]["bits"])
            # wght_quant = quant.select_func(quant_data)(wght_arr)
            bg_quant = np.array(bg_q).reshape(b_len, -1).tolist()

        count_iter = fast.filter1d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points) * len(fast_conv)
    elif dim == 2:
        points, c, b, a, q = read_build_2d(repo)
        conv_func = (
            fast.conv2d if len(quant_data) == 0 else quant.select_conv2d(quant_data)
        )
        fast_conv = conv_func(wght_arr, c[0], q[0], b[0], a[0], c[1], q[1], b[1], a[1])
        output_fast = fast.filter2d_slide2d(
            fast_conv, feat_arr, output_default.shape, c_len, a_len
        )
        count_iter = fast.filter2d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points[0]) * len(points[1])
        bg = fast.g_to_bg2d(q[0], b[0], q[1], b[1], wght_arr)
        if len(quant_data) == 0:
            bg_quant = bg
        else:
            wght_quant = quant.select_func(quant_data)(wght_arr)
            bg_quant = fast.g_to_bg2d(q[0], b[0], q[1], b[1], wght_quant)

    if len(quant_data) != 0:
        metric = r2_score(output_default.reshape(-1), output_fast.reshape(-1))
        text_metric = f"R2: {metric}%\n"
    else:
        metric = np.all(output_default == output_fast)
        text_metric = f"Output default and fast are equals: {metric}\n"

    size = output_default.size
    text = (
        f"Feature: {feature_random}\n"
        f"Weights: {weight_random}\n"
        f"Image side: {image_side}\n"
        f"{text_equal}"
        f"{text_metric}"
        "Totals\n"
        "Naive\n"
        f"Convolutions: {size}\n"
        f"Multiplications: {size * 9}\n"
        f"Additions: {size * 8}\n"
        "Fast\n"
        f"Convolutions: {count_iter}\n"
        f"Multiplications: {count_mult}\n"
    )

    if len(suffix) > 0:
        path = repo.dir_sim / f"rand-{suffix}"
    else:
        path = repo.dir_sim / "rand"

    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", "w") as f:
        f.write(text)

    for arr, name in zip(
        [feat_arr, wght_arr, output_default, output_fast], ["d", "g", "s_default", "s"]
    ):
        np.savetxt(path / f"{name}.txt", arr, fmt="%d")

    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    list_array = [
        {"name": "weight", "value": wght_arr},
        {"name": "weight_gg", "value": bg},
        {"name": "weight_gg_quant", "value": bg_quant},
        {"name": "feat_in", "value": feat_arr},
        {"name": "gold", "value": output_default},
        {"name": "gold_quant", "value": output_fast},
    ]
    quant_dict = (
        {f"QUANT_{k}".upper(): v for k, v in quant_data["params"].items()}
        if len(quant_data) > 0
        else {}
    )
    dict_def = {
        "QUANT": quant_data["func"].upper() if len(quant_data) > 0 else None,
        **quant_dict,
        "W_SIZE": wght_arr.shape[0],
        "FIN_SIZE": feat_arr.shape[0],
        "FOUT_SIZE": output_fast.shape[0],
    }

    arr = [{**r, "type": "int"} for r in list_array]
    utils.c_header(repo.dir_clib_data / "sim.h", arr, dict_def)

    arr = [{**r, "type": "float"} for r in list_array]
    utils.c_header(repo.dir_clib_data_float / "sim_float.h", arr, dict_def)

    out_dict = {"quant": len(quant_data) > 0, "metric": metric, "text": text}
    return out_dict


def cmd_example_random(repo, feature, weight, suffix):
    dim, c_len, b_len, a_len = read_init(repo)
    repo.dir_example.mkdir(parents=True, exist_ok=True)

    if len(suffix) > 0:
        name = repo.dir_example / f"example-random-{suffix}"
    else:
        name = repo.dir_example / "example-random"

    if dim == 1:
        f = np.random.randint(feature[0], feature[1], size=c_len)
        d = sy.Matrix(f)
        w = np.random.randint(weight[0], weight[1], size=b_len)
        g = sy.Matrix(w)
    elif dim == 2:
        f0 = np.random.randint(feature[0], feature[1], size=c_len[0] * c_len[1])
        f = np.array(f0).reshape(c_len[0], c_len[1])
        d = sy.Matrix(f)
        w0 = np.random.randint(weight[0], weight[1], size=b_len[0] * b_len[1])
        w = np.array(w0).reshape(b_len[0], b_len[1])
        g = sy.Matrix(w)

    if dim == 1:
        points, c, b, a, q = read_build_1d(repo)
        latex.example_1d(b, c, a, g, d, q, name)
        repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
        bg = fast.g_to_bg(q, b, g)
        list_array = [
            {"name": "md", "type": "int", "value": d},
            {"name": "mg", "value": g},
            {"name": "mgg", "value": bg},
        ]
        arr = [{**r, "type": "int"} for r in list_array]
        utils.c_header(repo.dir_clib_data / "example.h", arr, {})

        arr = [{**r, "type": "float"} for r in list_array]
        utils.c_header(repo.dir_clib_data_float / "example_float.h", arr, {})

    elif dim == 2:
        data_bind = read_bind_if_exists(repo)
        init_data = read_init(repo)
        build_data = read_build_2d(repo)

        if data_bind["func"] == "iterate":
            latex.example_2d_bind_iterate(init_data, build_data, d, g, name)
        if data_bind["func"] == "nest":
            latex.example_2d_bind_nest(init_data, build_data, d, g, name)

        (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
        bg = fast.g_to_bg2d(q1, b1, q2, b2, g)
        repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
        list_array = [
            {"name": "md", "value": d},
            {"name": "mg", "value": g},
            {"name": "mgg", "value": bg},
        ]

        arr = [{**r, "type": "int"} for r in list_array]
        utils.c_header(repo.dir_clib_data / "example.h", arr, {})

        arr = [{**r, "type": "float"} for r in list_array]
        utils.c_header(repo.dir_clib_data_float / "example_float.h", arr, {})


def cmd_example_sequential(repo, feature, weight, suffix):
    dim, c_len, b_len, a_len = read_init(repo)
    repo.dir_example.mkdir(parents=True, exist_ok=True)
    if len(suffix) > 0:
        name = repo.dir_example / f"example-seq-{suffix}"
    else:
        name = repo.dir_example / "example-seq"
    if dim == 1:
        f = np.arange(feature, feature + c_len)
        d = sy.Matrix(f)
        w = np.arange(weight, weight + b_len)
        g = sy.Matrix(w)
        s = utils.default_convolve(d, g)
    elif dim == 2:
        f0 = np.arange(feature, feature + c_len[0] * c_len[1])
        f = np.array(f0).reshape(c_len[0], c_len[1])
        d = sy.Matrix(f)
        w0 = np.arange(weight, weight + b_len[0] * b_len[1])
        w = np.array(w0).reshape(b_len[0], b_len[1])
        g = sy.Matrix(w)
        s = utils.default_convolve(d, g)

    if dim == 1:
        points, c, b, a, q = read_build_1d(repo)
        latex.example_1d(b, c, a, g, d, q, name)
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

    elif dim == 2:
        data_bind = read_bind_if_exists(repo)
        init_data = read_init(repo)
        build_data = read_build_2d(repo)
        if data_bind["func"] == "iterate":
            latex.example_2d_bind_iterate(init_data, build_data, d, g, name)
        if data_bind["func"] == "nest":
            latex.example_2d_bind_nest(init_data, build_data, d, g, name)

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

        arr = [{**r, "type": "float"} for r in list_array]
        utils.c_header(repo.dir_clib_data_float / "example_float.h", arr, {})
