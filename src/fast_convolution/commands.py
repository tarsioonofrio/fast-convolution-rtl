import os
import json
import shutil
from pathlib import Path
from datetime import datetime

import click
import numpy as np
import sympy as sy
import pylatex as tex
from PIL import Image
from scipy import signal
from sklearn import metrics
# from matplotlib import pyplot as plt

from . import fast
from . import quant
from . import latex
from .naive import naive_convolve
from .utils import c_header


root_path = Path(os.getcwd())
dir_config = root_path / "config"
file_init = dir_config / "init.json"
file_build = dir_config / "build.json"
file_bind = dir_config / "bind.json"
file_quant = dir_config / "quant.json"
dir_build = root_path / "build"
dir_quant = root_path / "quant"
dir_example = root_path / "example"
dir_sim = root_path / "sim"
dir_lib = root_path / "lib"


def read_init():
    with open(file_init) as f:
        data = json.load(f)
    c = data["c"]
    a = data["a"]
    b = data["b"]
    dim = data["dim"]
    return dim, c, b, a


def read_build_1d():
    with open(file_build) as f:
        data = json.load(f)
    p = data["p"]
    c = sy.Matrix(data["c"])
    b = sy.Matrix(data["b"])
    a = sy.Matrix(data["a"])
    q = sy.Matrix([
        sy.Rational(p, q) for p, q in data["q"]
    ])
    return p, c, b, a, q


def read_build_2d():
    with open(file_build) as f:
        data = json.load(f)
    p = sy.Matrix(data["p"][0]), sy.Matrix(data["p"][1])
    c = sy.Matrix(data["c"][0]), sy.Matrix(data["c"][1])
    b = sy.Matrix(data["b"][0]), sy.Matrix(data["b"][1])
    a = sy.Matrix(data["a"][0]), sy.Matrix(data["a"][1])
    q = [
        sy.Matrix([sy.Rational(p, q) for p, q in d])
        for d in data["q"]
    ]
    return p, c, b, a, q


def read_init_if_exists():
    if file_init.exists() is False:
        return {}
    with open(file_init) as f:
        data = json.load(f)
    return data


def read_num_points():
    if file_init.exists() is False:
        return 1
    dim, c, b, a = read_init()
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
    p0 = [p*s for s in range(1, size//2 + size % 2) for p in [1, -1]]
    p = [0] + p0[:size-1 - size % 2] + ['inf']
    return p


def default_toom_cook_points2d(size0, axis=None):
    if isinstance(size0, list) is False:
        return 1
    size = size0[axis]
    p0 = [p*s for s in range(1, size//2 + size % 2) for p in [1, -1]]
    p = [0] + p0[:size-1 - size % 2] + ['inf']
    return p


def read_quant_if_exists():
    if file_quant.exists() is False:
        return {}
    with open(file_quant) as f:
        data = json.load(f)
    return data


def now():
    return datetime.now().strftime('%Y%m%d-%H%M')


def write_bind(func, params=None):
    data = {
        "func": func,
        "params": params
    }
    with open(file_bind, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_bind_if_exists():
    if file_bind.exists() is False:
        return {}
    with open(file_bind) as f:
        data = json.load(f)
    return data


def cmd_init(dimensions, in_len, out_len, w):
    if file_init.exists():
        click.echo(
            message="init.json existis, fconv model already initialized"
        )
        click.Abort()
        click.echo(file_init)
        exit(1)
    in_arr = np.array(in_len)
    w_arr = np.array(w)
    out_arr = np.array(out_len)
    if in_len is None and out_len is None:
        b = in_arr - out_arr + 1
        c = in_arr
        a = out_arr
    elif in_len is None:
        c = out_arr + w_arr - 1
        a = out_arr
        b = w_arr
    elif out_len is None:
        a = in_arr - w_arr + 1
        c = in_arr
        b = w_arr
    else:
        click.echo(
            message="Just one param is passed, inform another."
        )
        click.Abort()
        exit(1)

    data = {
        "dim": dimensions,
        "c": c.tolist(),
        "a": a.tolist(),
        "b": b.tolist(),
    }
    file_init.parent.mkdir(parents=True, exist_ok=True)
    with open(file_init, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    dir_lib.mkdir(parents=True, exist_ok=True)
    init_path = dir_lib / "init.h"
    if dimensions == 1:
        dict_defs = {
            "A_SIZE": a,
            "B_SIZE": b,
            "C_SIZE": c,
        }
        c_header(init_path, [], dict_defs)


def cmd_show(init, build, quant):
    init_data = read_init_if_exists()
    if file_init.exists():
        if init:
            click.echo(read_init_if_exists())
        if build and file_build.exists():
            if init_data["dim"] == 1:
                click.echo(read_build_1d())
            elif init_data["dim"] == 2:
                click.echo(read_build_2d())
        if quant and file_quant.exists():
            click.echo(read_quant_if_exists())


def cmd_build_toom_cook1d(points):
    dim, c_len, b_len, a_len = read_init()
    # at_len = ct_len + b_len - 1
    list_points = [np.inf if p == 'inf' else int(p) for p in points]

    c, q, b, a = fast.toom_cook(a_len, b_len, list_points)
    d = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c_len))))
    g = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b_len))))
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
    with open(file_build, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    dir_build.mkdir(parents=True, exist_ok=True)
    path = dir_build / "convolution"
    latex.build_1d(b, c, a, g, d, sy.Matrix(q), path)
    a_sum = fast.count_sums(a)
    c_sum = fast.count_sums(c)
    text = (
        f"Total multiplications: {(b_len)}\n"
        f"Sums:\n"
        f"A: {a_sum}\n"
        f"C: {c_sum}\n"
        f"Total: {a_sum + c_sum}\n"
    )
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)
    fast.write_csa_parcels(a, c, path / "csa")

    dir_lib.mkdir(parents=True, exist_ok=True)
    init_path = dir_lib / "build.h"
    if dim == 1:
        list_array = [
            {"name": "mct", "type": "int", "value": np.array(c, dtype=int).T.tolist(), "shape": np.array(c.T, dtype=int).shape},
            {"name": "mb", "type": "int", "value": np.array(b, dtype=int).tolist(), "shape": np.array(b, dtype=int).shape},
            {"name": "mat", "type": "int", "value": np.array(a, dtype=int).T.tolist(), "shape": np.array(a.T, dtype=int).shape},
            {"name": "mq", "type": "int", "value": qr, "shape": np.array(qr, dtype=int).shape},
        ]
        c_header(init_path, list_array, {})


def cmd_build_toom_cook2d(points1d, points2d):
    dim, c_len, b_len, a_len = read_init()
    # at_len = ct_len + b_len - 1
    list_points1d = [np.inf if p == 'inf' else int(p) for p in points1d]
    list_points2d = [np.inf if p == 'inf' else int(p) for p in points2d]

    c1, q1, b1, a1 = fast.toom_cook(a_len[0], b_len[0], list_points1d)
    di1 = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c_len[0]))))
    g1 = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b_len[0]))))
    bg1 = fast.g_to_bg(q1, b1, g1)
    qr1 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q1
    ]

    c2, q2, b2, a2 = fast.toom_cook(a_len[1], b_len[1], list_points2d)
    di2 = sy.Matrix(sy.symbols(" ".join(f"d_{i}"for i in range(c_len[1]))))
    g2 = sy.Matrix(sy.symbols(" ".join(f"g_{i}"for i in range(b_len[1]))))
    bg2 = fast.g_to_bg(q2, b2, g2)
    qr2 = [
        [int(i.p), int(i.q)] if isinstance(i, sy.Rational) else [int(i), 1]
        for i in q2
    ]

    data = {
        "p": [list_points1d, list_points2d],
        "c": [np.array(c1, dtype=int).tolist(), np.array(c2, dtype=int).tolist()],
        "q": [qr1, qr2],
        "b": [np.array(b1, dtype=int).tolist(), np.array(b2, dtype=int).tolist()],
        "a": [np.array(a1, dtype=int).tolist(), np.array(a2, dtype=int).tolist()],
    }
    with open(file_build, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    dir_build.mkdir(parents=True, exist_ok=True)
    path1 = dir_build / "convolution-axis1"
    latex.build_1d(b1, c1, a1, g1, di1, q1, path1)
    path2 = dir_build / "convolution-axis2"
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
    path = dir_build / "convolution-axis"
    with open(f"{path}_info.txt", "w") as f:
        f.write(text)


def cmd_build2d_bind_iterate():
    path = dir_build / "bind-iterated"
    path.mkdir(parents=True, exist_ok=True)
    init_data = read_init()
    build_data = read_build_2d()
    write_bind("iterate")
    latex.build_2d_bind_iterated(init_data, build_data, path)


def cmd_build2d_bind_nest():
    path = dir_build / "bind-nest"
    path.mkdir(parents=True, exist_ok=True)
    init_data = read_init()
    build_data = read_build_2d()
    write_bind("nest")
    latex.build_2d_bind_nest(init_data, build_data, path)

    (p1, p2), (c1, c2), (b1, b2), (a1, a2), (q1, q2) = build_data
    a = np.kron(a1, a2)
    c = np.kron(c1, c2)
    fast.write_csa_parcels(a, c, path / "csa")


def cmd_quant_none():
    file_quant.unlink(missing_ok=True)


def cmd_quant_shift(bits):
    data = {
        "func": "shift",
        "params": {
            "bits": bits
        }
    }
    with open(file_quant, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def cmd_sim_file(feature, weight):
    dim, c_len, b_len, a_len = read_init()
    quant_data = read_quant_if_exists()
    with open(feature) as f:
        image = Image.open(feature).convert('L')
        feat_arr = np.array(image)
    with open(weight) as f:
        if dim == 1:
            wght_arr = (np.array(json.load(f)).reshape(b_len, b_len))
        elif dim == 2:
            wght_arr = (np.array(json.load(f)).reshape(b_len[0], b_len[1]))

    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode='valid'
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    text_equal = f"Output default and naive are equals: {compare_naive}\n"

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        conv_func = (
            fast.conv1d if len(quant_data) == 0
            else quant.select_func1d(quant_data)
        )
        fast_conv = [
            conv_func(
                wght_arr[i], c, q, b, a
            )
            for i in range(b_len)
        ]

        output_fast = np.sum(axis=0, a=[
            fast.filter1d_slide2d(
                fast_conv[i], feat_arr, output_default.shape, i, c_len,
                a_len
            )
            for i in range(0, wght_arr.shape[0])
         ])
        count_iter = fast.filter1d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points) * len(fast_conv)
    elif dim == 2:
        points, c, b, a, q = read_build_2d()
        conv_func = (
            fast.conv2d if len(quant_data) == 0
            else quant.select_func2d(quant_data)
        )
        fast_conv = conv_func(
            wght_arr, c[0], q[0], b[0], a[0], c[1], q[1], b[1], a[1]
        )
        output_fast = fast.filter2d_slide2d(
            fast_conv, feat_arr, output_default.shape, c_len, a_len
        )
        count_iter = fast.filter2d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points[0]) * len(points[1])

    if len(quant_data) != 0:
        r2 = metrics.r2_score(
            output_default.reshape(-1), output_fast.reshape(-1)
        )
        text_metric = (f"R2: {r2}\n")
    else:
        compare_fast = np.all(output_default == output_fast)
        text_metric = f"Output default and fast are equals: {compare_fast}\n"

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
    path = dir_sim / f"file-{now()}"
    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", 'w') as f:
        f.write(text)

    for arr, name in ((feat_arr, "d"), (wght_arr, "g")):
        np.savetxt(path / f"{name}.txt", arr, fmt='%d')

    dir_lib.mkdir(parents=True, exist_ok=True)
    init_path = dir_lib / "sim.h"
    list_array = [
        {"name": "weight", "type": "int", "value": wght_arr.tolist(), "shape": wght_arr.shape},
        {"name": "feat_in", "type": "int", "value": feat_arr.tolist(), "shape": feat_arr.shape},
        {"name": "gold", "type": "int", "value": output_fast.tolist(), "shape": output_fast.shape},
    ]
    dict_def = {
        "W_SIZE": wght_arr.shape[0],
        "FIN_SIZE": feat_arr.shape[0],
        "FOUT_SIZE": output_fast.shape[0],
    }
    c_header(init_path, list_array, dict_def)

    return text



def cmd_sim_random(feature_random, weight_random, image_side, loop):
    dim, c_len, b_len, a_len = read_init()
    quant_data = read_quant_if_exists()
    feat = np.random.randint(
         feature_random[0], feature_random[1], size=image_side ** 2
     )
    feat_arr = feat.reshape(image_side, image_side)

    if dim == 1:
        wght = np.random.randint(
            weight_random[0], weight_random[1], size=b_len ** 2
        )
        wght_arr = wght.reshape(b_len, b_len)
    elif dim == 2:
        wght = np.random.randint(
            weight_random[0], weight_random[1],
            size=b_len[0] * b_len[1]
        )
        wght_arr = wght.reshape(b_len[0], b_len[1])

    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode='valid'
    )
    output_naive = naive_convolve(feat_arr, wght_arr)
    compare_naive = np.all(output_default == output_naive)
    text_equal = f"Output default and naive are equals: {compare_naive}\n"

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        conv_func = (
            fast.conv1d if len(quant_data) == 0
            else quant.select_func1d(quant_data)
        )
        fast_conv = [
            conv_func(
                wght_arr[i], c, q, b, a
            )
            for i in range(b_len)
        ]

        output_fast = np.sum(axis=0, a=[
            fast.filter1d_slide2d(
                fast_conv[i], feat_arr, output_default.shape, i, c_len,
                a_len
            )
            for i in range(0, wght_arr.shape[0])
         ])
        count_iter = fast.filter1d_slide2d_count(output_default.shape, a_len)
        count_mult = count_iter * len(points) * len(fast_conv)
    elif dim == 2:
        points, c, b, a, q = read_build_2d()
        conv_func = (
            fast.conv2d if len(quant_data) == 0
            else quant.select_func2d(quant_data)
        )
        fast_conv = conv_func(
            wght_arr, c[0], q[0], b[0], a[0], c[1], q[1], b[1], a[1]
        )
        output_fast = fast.filter2d_slide2d(
            fast_conv, feat_arr, output_default.shape, c_len, a_len
        )
        count_iter = fast.filter2d_slide2d_count(
            output_default.shape, a_len
        )
        count_mult = count_iter * len(points[0]) * len(points[1])

    if len(quant_data) != 0:
        r2 = metrics.r2_score(
            output_default.reshape(-1), output_fast.reshape(-1)
        )
        text_metric = (f"R2: {r2}%\n")
    else:
        compare_fast = np.all(output_default == output_fast)
        text_metric = f"Output default and fast are equals: {compare_fast}\n"

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
    path = dir_sim / f"random-{now()}"
    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", 'w') as f:
        f.write(text)
 
    for arr, name in ((feat_arr, "d"), (wght_arr, "g")):
        np.savetxt(path / f"{name}.txt", arr, fmt='%d')

    return text


def cmd_example_random(feature, weight):
    dim, c_len, b_len, a_len = read_init()
    dir_example.mkdir(parents=True, exist_ok=True)

    if dim == 1:
        f = np.random.randint(
            feature[0], feature[1], size=c_len
        )
        d = sy.Matrix(f)
        w = np.random.randint(
            weight[0], weight[1], size=b_len
        )
        g = sy.Matrix(w)
    elif dim == 2:
        f0 = np.random.randint(
            feature[0], feature[1], size=c_len[0]*c_len[1]
        )
        f = np.array(f0).reshape(c_len[0], c_len[1])
        d = sy.Matrix(f)
        w0 = np.random.randint(
            weight[0], weight[1], size=b_len[0] * b_len[1]
        )
        w = np.array(w0).reshape(b_len[0], b_len[1])
        g = sy.Matrix(w)

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        latex.example_1d(
            b, c, a, g, d, q, dir_example / f"example-random-{now()}"
        )

    elif dim == 2:
        data_bind = read_bind_if_exists()
        if data_bind["func"] == "iterate":
            latex.example_2d_bind_iterate(
                read_init(), read_build_2d(), d, g,
                dir_example / f"example-random-{now()}"
            )
        if data_bind["func"] == "nest":
            latex.example_2d_bind_nest(
                read_init(), read_build_2d(), d, g,
                dir_example / f"example-random-{now()}"
            )


def cmd_example_sequential(feature, weight):
    dim, c_len, b_len, a_len = read_init()
    dir_example.mkdir(parents=True, exist_ok=True)

    if dim == 1:
        f = np.arange(feature, feature + c_len)
        d = sy.Matrix(f)
        w = np.arange(weight, weight + b_len)
        g = sy.Matrix(w)
    elif dim == 2:
        f0 = np.arange(feature, feature + c_len[0]*c_len[1])
        f = np.array(f0).reshape(c_len[0], c_len[1])
        d = sy.Matrix(f)
        w0 = np.arange(weight, weight + b_len[0] * b_len[1])
        w = np.array(w0).reshape(b_len[0], b_len[1])
        g = sy.Matrix(w)

    if dim == 1:
        points, c, b, a, q = read_build_1d()
        latex.example_1d(
            b, c, a, g, d, q, dir_example / f"example-seq-{now()}"
        )
        dir_lib.mkdir(parents=True, exist_ok=True)
        init_path = dir_lib / "example.h"
        list_array = [
            {"name": "md", "type": "int", "value": np.array(d, dtype=int).tolist(), "shape": np.array(d, dtype=int).shape},
            {"name": "mg", "type": "int", "value": np.array(g, dtype=int).tolist(), "shape": np.array(g, dtype=int).shape},
        ]
        c_header(init_path, list_array, {})

    elif dim == 2:
        data_bind = read_bind_if_exists()
        if data_bind["func"] == "iterate":
            latex.example_2d_bind_iterate(
                read_init(), read_build_2d(), d, g,
                dir_example / f"example-seq-{now()}"
            )
        if data_bind["func"] == "nest":
            latex.example_2d_bind_nest(
                read_init(), read_build_2d(), d, g,
                dir_example / f"example-seq-{now()}"
            )
