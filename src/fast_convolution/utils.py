import os
from pathlib import Path

import numpy as np
import sympy as sy
from PIL import Image, ImageOps
from scipy import signal


def plot_pdf(
    page,
    crop_float=None,
    dpi=200,
):
    """
    (upper, lower)
    crop float value between 0 and 1
    """
    from IPython.core.display_functions import display

    pix = page.get_pixmap(dpi=dpi)
    # mode = "RGBA" if pix.alpha else "RGB"
    mode = "RGB"
    image = ImageOps.invert(
        Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    )
    if crop_float is None:
        display(image)
    else:
        assert 0 <= crop_float[0] <= 1
        assert 0 <= crop_float[1] <= 1
        # assert 0 <= crop_float[2] <= 1
        # assert 0 <= crop_float[3] <= 1
        left = 0
        upper = int(pix.height * crop_float[0])
        right = pix.width
        lower = int(pix.height * crop_float[1])
        crop = (left, upper, right, lower)
        display(image.crop(crop))


def plot_pdf2col(page, column, crop_float=None, dpi=200):
    """
    (upper, lower)
    crop float value between 0 and 1
    """
    from IPython.core.display_functions import display

    pix = page.get_pixmap(dpi=dpi)
    # mode = "RGBA" if pix.alpha else "RGB"
    mode = "RGB"
    image = ImageOps.invert(
        Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    )
    if crop_float is None:
        display(image)
    else:
        assert 0 <= crop_float[0] <= 1
        assert 0 <= crop_float[1] <= 1
        assert column in [0, 1]
        left = (pix.width) // 2 * column
        upper = int(pix.height * crop_float[0])
        right = (pix.width) // 2 * (column + 1)
        lower = int(pix.height * crop_float[1])
        crop = (left, upper, right, lower)
        display(image.crop(crop))


def symmetrical_polynomial_factorization(polynomial, di, gi):
    quo, rem = np.divmod(len(polynomial.args), 2)
    if rem == 0:
        args = polynomial.args
    else:
        if len(gi) % 2 == 0 and len(di) % 2 == 0:
            args = [i for e, i in enumerate(polynomial.args)]
        else:
            args = [
                i
                for e, i in enumerate(polynomial.args)
                if sum([quo, rem]) - 1 != e
            ]
    pol_idx = [e for e, c in enumerate(di) for d in args if d.coeff(c, 1) != 0]
    prod = np.prod([np.sum([(c[i]) for i in pol_idx]) for c in [di, gi]])
    s = prod - (prod.expand() - polynomial)
    return s


def symmetrical_cyclic_convolution(x, y):
    # https://stackoverflow.com/a/66709258
    x_arr = np.array(x)
    size = x_arr.shape[0]
    xx = np.tile(x_arr.reshape(-1), 2)
    yy = np.array(y).reshape(-1)
    out = np.convolve(xx, yy)
    out_clip = out[size : 2 * size]
    out_mtx = sy.Matrix(out_clip)
    return out_mtx


def winograd_cyclic_conv2x2(x, y):
    ax0 = x[0] + x[1]
    ax1 = x[0] - x[1]
    bx0 = (y[0] + y[1]) / 2
    bx1 = (y[0] - y[1]) / 2

    m0 = ax0 * bx0
    m1 = ax1 * bx1
    s0 = m0 + m1
    s1 = m0 - m1
    return (s0, s1)


# https://stackoverflow.com/a/38034801
def conv_circ_fft(signal, kernel):
    """
    signal: real 1D array
    ker: real 1D array
    signal and ker must have same shape
    """
    return np.real(np.fft.ifft(np.fft.fft(signal) * np.fft.fft(kernel)))


def c_header(path, list_array, dict_defs):
    name = path.stem.upper()
    source_str = (
        f"#ifndef C_{name}_H\n"
        f"#define C_{name}_H\n\n"
        "{code}\n"
        f"#endif //C_{name}_H\n"
    )
    array_str = "const {type} {name}[{size}] = {{\n" "{value}\n" "}};\n"
    def_str = "#define {key} {value}\n"
    list_def = []
    if len(dict_defs) > 0:
        for k, v in dict_defs.items():
            definition = def_str.format(key=k, value=v)
            list_def.append(definition)

    list_data = []
    if len(list_array) > 0:
        for array in list_array:
            typ = array["type"]
            name = array["name"]
            np_arr = np.array(array["value"]).astype(typ)
            shape = np_arr.shape
            value = np_arr.tolist()
            if typ == "float":
                value_str = (",\n").join(
                    [
                        "\t" + ", ".join(map(lambda x: str(x) + "f", v))
                        for v in value
                    ]
                )
            else:
                value_str = (",\n").join(
                    ["\t" + ", ".join(map(str, v)) for v in value]
                )
            size = "*".join(map(str, shape))
            array = array_str.format(
                type=typ, name=name, value=value_str, size=size
            )
            list_data.append(array)

    list_def_data = list_def + ["\n"] + list_data
    source = source_str.format(code="".join(list_def_data))
    with open(path, "w") as f:
        f.write(source)


def sv_pkg(path, list_array, dict_defs):
    name = path.stem
    source_str = (
        f"package {name};\n\n"
        "  timeunit 1ns;\n"
        "  timeprecision 1ps;\n\n"
        "{code}\n"
        f"endpackage\n"
    )
    array_str = "  const {type} {name} = '{{\n" "{value}\n  }};\n"
    def_str = "  localparam int {key} = {value};\n"
    list_def = []
    if len(dict_defs) > 0:
        for k, v in dict_defs.items():
            definition = def_str.format(key=k, value=v)
            list_def.append(definition)

    list_data = []
    if len(list_array) > 0:
        for array in list_array:
            typ = array["type"]
            name = array["name"]
            np_arr = np.array(array["value"]).astype(typ)
            shape = np_arr.shape
            value = np_arr.tolist()
            value_str = (",\n").join(
                ["    '{" + ", ".join(map(str, v)) + "}" for v in value]
            )
            size = "*".join(map(str, shape))
            array = array_str.format(
                type=typ, name=name, value=value_str, size=size
            )
            list_data.append(array)

    list_def_data = list_def + ["\n"] + list_data
    source = source_str.format(code="".join(list_def_data))
    with open(path, "w") as f:
        f.write(source)


def c_shift(d, s, z):
    if s < 0:
        signal = "-"
    else:
        signal = "+"

    if z == 0:
        return f" {signal} {d}"
    else:
        return f" {signal} ({d} << {z})"


def c_matmul_shift_noloop(mtx, name_suffix):
    mtx_log = log2_lst(mtx)
    var_in = [f"m_in[{i}]" for i in range(mtx.shape[1])]
    var_out = [f"m_out[{i}]" for i in range(mtx.shape[0])]

    lst_data = [
        [
            [c_shift(d, num["s"], z) for z in num["z"]]
            for d, num in zip(var_in, row)
            if "s" in num
        ]
        for row in mtx_log
    ]
    lst_join = ["".join(["".join(num) for num in row]) for row in lst_data]
    lst_output = [f"\t{m} = {d};" for m, d in zip(var_out, lst_join)]
    lst_str = "\n".join(lst_output)
    header = f"void matrix_mul_shift_noloop_{name_suffix}(int *m_out, const int *m_in)"
    function = f"{header}{{\n" f"{lst_str}\n" "}\n"
    return {"header": f"{header};\n", "function": function}


def c_matmul_shift_noloop_nest(mtx1, name_suffix, in_shp, out_shp, swap=False):
    mtx1_log = log2_lst(mtx1)
    mtx2 = np.array(
        [f"m_in[{i}]" for i in range(in_shp[0] * in_shp[1])]
    ).reshape(*in_shp)
    mtx3 = (
        matmul(mtx2, np.array(mtx1_log))
        if swap
        else matmul(np.array(mtx1_log), mtx2)
    )
    var_out = [f"m_out[{i}]" for i in range(out_shp[0] * out_shp[1])]

    lst_data = [
        [
            c_shift(k, v["s"], z)
            for shift in data
            for k, v in shift.items()
            if "s" in v
            for z in v["z"]
        ]
        for data in mtx3
    ]

    lst_join = ["".join(["".join(num) for num in row]) for row in lst_data]
    lst_output = [f"\t{m} = {d};" for m, d in zip(var_out, lst_join)]
    lst_str = "\n".join(lst_output)
    header = f"void matrix_mul_shift_noloop_{name_suffix}(int *m_out, const int *m_in)"
    function = f"{header}{{\n" f"{lst_str}\n" "}\n"
    return {"header": f"{header};\n", "function": function}


def c_hadamart_product_nollop(out_size, suffix=""):
    lst = [f"\tout[{i}] = in1[{i}] * in2[{i}];" for i in range(out_size)]
    lst_str = "\n".join(lst)
    header = f"void hadamart_product_noloop{suffix}(int *out, const int *in1, const int *in2)"
    function = f"{header}{{\n" f"{lst_str}\n" "}\n"
    return {"header": f"{header};\n", "function": function}


def default_convolve(f, w):
    output_default = signal.convolve(f, w[::-1, ::-1], mode="valid")
    return output_default


def matmul(m1, m2):
    row1 = m1.shape[0]
    col2 = m2.shape[1]
    col2_row1 = m1.shape[1]
    in1 = m1.reshape(-1)
    in2 = m2.reshape(-1)
    out = [[] for _ in range(row1 * col2)]
    for r in range(row1):
        for c in range(col2):
            for k in range(col2_row1):
                d1 = in1[r * col2_row1 + k]
                d2 = in2[k * col2 + c]
                data = {d2: d1} if isinstance(d2, str) else {d1: d2}
                out[r * col2 + c] += [data]
    return out


def _recursive_log2(n):
    return [e for e, b in enumerate(bin(n)[2::][::-1]) if b == "1"]


def recursive_log2(n):
    if n == 0:
        return {}
    sign = -1 if n < 0 else 1
    if isinstance(n, sy.Integer):
        exp_z = _recursive_log2(n)
        out = {"s": sign, "z": exp_z}
    else:
        exp_p = _recursive_log2(n.p)
        exp_q = _recursive_log2(n.q)
        out = {
            "s": sign,
            "p": exp_p,
            "q": exp_q,
        }
    return out


def log2_lst(mtx):
    lst_in = mtx.tolist()
    lst_out = [
        [None for c in range(len(lst_in[0]))] for r in range(len(lst_in))
    ]
    for r, row in enumerate(lst_in):
        for c, col in enumerate(row):
            lst_out[r][c] = recursive_log2(col)
    return lst_out


def log2_matrix(lst):
    def log2_rational(p, q):
        p0 = sy.UnevaluatedExpr(sy.Pow(2, p, evaluate=False))
        q0 = sy.Pow(
            sy.UnevaluatedExpr(sy.Pow(2, q, evaluate=False)), -1, evaluate=False
        )
        return p0 * q0

    mtx = sy.zeros(len(lst), len(lst[0]))
    for er, r in enumerate(lst):
        for ec, c in enumerate(r):
            if "z" in c:
                n = sum(
                    [
                        c["s"]
                        * sy.UnevaluatedExpr(sy.Pow(2, z, evaluate=False))
                        for z in c["z"]
                    ]
                )
            elif "p" in c:
                p = sum(
                    [
                        (
                            c["s"]
                            * sy.UnevaluatedExpr(sy.Pow(2, p, evaluate=False))
                        )
                        for p in c["p"]
                    ]
                )
                # q = sum([
                #     (c["s"] * sy.Pow(sy.UnevaluatedExpr(
                #         sy.Pow(2, q, evaluate=False)), -1, evaluate=False)
                #      )
                #     for q in c["q"]
                # ])
                if len(c["q"]) == 1:
                    _q = sy.UnevaluatedExpr(
                        sy.Pow(2, c["q"][0], evaluate=False)
                    )
                    q = sy.Pow(_q, -1, evaluate=False)
                else:
                    q = c["q"]
                n = p * q
            else:
                n = 0
            mtx[er, ec] = n
    return mtx


def matrix_to_log2(mtx):
    return log2_matrix(log2_lst(mtx))


def count_sums(mtx):
    m_log = matrix_to_log2(mtx)
    m_sum = [
        [1 if -1 in m.args else len(m.args) for m in r] for r in m_log.tolist()
    ]
    return np.sum(m_sum)


def csa_lst(mtx, positive=True):
    lst = log2_lst(mtx)
    signal = 1 if positive else -1
    max_pow = max_power(lst, signal)
    max_lst = [
        [
            [
                1 if len(c) > 0 and p in c["z"] and c["s"] == signal else 0
                for c in r
            ]
            for r in lst
        ]
        for p in range(max_pow + 1)
    ]
    return max_lst


def max_power(lst, positive=True):
    signal = 1 if positive else -1
    max_pow = max(
        [0]
        + [
            max(
                [0]
                + [max(c["z"]) for c in r if len(c) > 0 and c["s"] == signal]
            )
            for r in lst
        ]
    )
    return max_pow


def csa_config(a, c):
    config = {
        (n, s): max_power(log2_lst(lst), positive=typ)
        for lst, n in zip([a.T, c.T], ["a", "c"])
        for typ, s in zip([True, False], ["p", "n"])
    }
    return config


def csa_config_nest(a1, a2, c1, c2):
    config = {
        (n, s): max_power(log2_lst(lst), positive=typ)
        for lst, n in zip([a1.T, a2.T, c1.T, c2.T], ["a", "A", "c", "C"])
        for typ, s in zip([True, False], ["p", "n"])
    }
    return config


def write_csa_config(config, path):
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "config.txt", "w") as f:
        for (n, s), p in config.items():
            f.write(f"{p} {n} {s}\n")


def csa_parcels(a, c):
    return {
        (n, s): csa_lst(lst, positive=typ)
        for lst, n in zip([a.T, c.T], ["a", "c"])
        for typ, s in zip([True, False], ["p", "n"])
    }


def csa_parcels_nest(a1, a2, c1, c2):
    return {
        (n, s): csa_lst(lst, positive=typ)
        for lst, n in zip([a1, a2.T, c1, c2.T], ["a1", "a2", "c1", "c2"])
        for typ, s in zip([True, False], ["p", "n"])
    }


def write_csa_parcels(csa, path):
    path.mkdir(parents=True, exist_ok=True)

    with open(path / "info.txt", "w") as f:
        for (n, s), lst in csa.items():
            f.write(f"{np.sum(lst)} {n} {s}\n")

    for (n, s), lst in csa.items():
        with open(path / f"{n}{s}.txt", "w") as f:
            for power in lst:
                for line in power:
                    f.write(" ".join(map(str, line)) + "\n")
                f.write("\n")


def is_two_power(n):
    return n > 0 and (n & (n - 1)) == 0


def matmul_sv(m1, m2):
    row1 = m1.shape[0]
    col2 = m2.shape[1]
    col2_row1 = m1.shape[1]
    in1 = m1.reshape(-1)
    in2 = m2.reshape(-1)
    out = [[] for _ in range(row1 * col2)]
    for r in range(row1):
        for c in range(col2):
            for k in range(col2_row1):
                d1 = in1[r * col2_row1 + k]
                d2 = in2[k * col2 + c]
                if isinstance(d1, str):
                    if d2 != 0:
                        out[r * col2 + c] += [d1]
                else:
                    if d1 != 0:
                        out[r * col2 + c] += [d2]
    return out


def matmul_sv2(m1, m2):
    row1 = m1.shape[0]
    col2 = m2.shape[1]
    col2_row1 = m1.shape[1]
    in1 = m1.reshape(-1)
    in2 = m2.reshape(-1)
    out1 = [[] for _ in range(row1 * col2)]
    out2 = [[] for _ in range(row1 * col2)]
    for r in range(row1):
        for c in range(col2):
            for k in range(col2_row1):
                d1 = in1[r * col2_row1 + k]
                d2 = in2[k * col2 + c]
                if d2 != 0:
                    out1[r * col2 + c] += [d1]
                if d1 != 0:
                    out2[r * col2 + c] += [d2]
    return [out1, out2]


def sv_bitshift(port, pow):
    return [
        f"{port}" if s == 0 else f"{port} <<< {s}" for s in _recursive_log2(pow)
    ]


def sv_nest(mtx, input_shp, name):
    # matrix C
    # name = "c"
    # input_shp = (5, 5)
    # mtx = sy.Matrix(
    #     [
    #         [2, 0, 0, 0, 0],
    #         [-1, -2, 2, -1, 2],
    #         [-2, -1, -3, 0, -1],
    #         [1, 1, 1, 1, -2],
    #         [0, 0, 0, 0, 1],
    #     ]
    # )
    matrix_idx = {
        "c": [0, 1],
        "a": [1, 0],
    }
    type_input = {
        "c": ["type_input", "type_matrix_c"],
        "a": ["type_weight", "type_matrix_a"],
    }
    type_output = {
        "c": ["type_matrix_c", "type_weight"],
        "a": ["type_matrix_a", "type_output"],
    }

    module1 = (
        f"module Matrix{name.upper()}{matrix_idx[name][0]}\n"
        "  import packConv::*;\n"
        "  (\n"
        f"    input  {type_input[name][0]} P,\n"
        f"    output {type_output[name][0]} soma\n"
        "  );\n"
        "  timeunit 1ns;\n"
        "  timeprecision 1ps;\n"
    )
    input1_str = np.array(
        [f"P[{i}]" for i in range(input_shp[0] * input_shp[1])]
    ).reshape(*input_shp)
    arr = np.array(mtx)
    arr_p = np.where(arr > 0, arr, 0)
    arr_n = np.where(arr < 0, arr, 0)

    port1_p, port1_pp_ = matmul_sv2(input1_str, arr_p)
    port1_pp = [[p for p in pp if p != 0] for pp in port1_pp_]
    signal_p1_str = (
        "  logic_vector "
        + ", ".join(f"sp{i}" for i in range(len(port1_p)))
        + ";"
    )

    csa1_p = []
    for idx, (lst_port, lst_pow) in enumerate(zip(port1_p, port1_pp)):
        pack_shift = [
            port if abs(pow) == 0 else sv_bitshift(port, pow)
            for port, pow in (zip(lst_port, lst_pow))
        ]
        lst_shift = [unpack for pack in pack_shift for unpack in pack]
        if len(lst_shift) == 0:
            pass
        elif len(lst_shift) == 1:
            csa1_p.append(f"  assign sp{idx} = {lst_shift[0]};")
        else:
            str_port = ", ".join(lst_shift)
            csa1_p.append(
                f"  CSA_{len(lst_shift)} csa_p{idx}({str_port}, sp{idx});"
            )
    port1_n, port1_np_ = matmul_sv2(input1_str, arr_n)
    port1_np = [[p for p in pp if p != 0] for pp in port1_np_]
    signal_n1_str = (
        "  logic_vector "
        + ", ".join(f"sn{i}" for i in range(len(port1_n)))
        + ";"
    )
    csa1_n = []
    for idx, (lst_port, lst_pow) in enumerate(zip(port1_n, port1_np)):
        pack_shift = [
            port if abs(pow) == 0 else sv_bitshift(port, pow)
            for port, pow in (zip(lst_port, lst_pow))
        ]
        lst_shift = [unpack for pack in pack_shift for unpack in pack]
        if len(lst_shift) == 0:
            pass
        elif len(lst_shift) == 1:
            csa1_n.append(f"  assign sn{idx} = {lst_shift[0]};")
        else:
            str_port = ", ".join(lst_shift)
            csa1_n.append(
                f"  CSA_{len(lst_shift)} csa_n{idx}({str_port}, sn{idx});"
            )

    port1_out = []
    for idx, (n, p) in enumerate(zip(port1_n, port1_p)):
        if len(p) > 0 and len(n) > 0:
            port1_out.append(f"  assign soma[{idx}] = sp{idx} - sn{idx};")
        elif len(p) > 0:
            port1_out.append(f"  assign soma[{idx}] = sp{idx};")
        elif len(n) > 0:
            port1_out.append(f"  assign soma[{idx}] = sn{idx};")

    m1_str = "\n".join(
        [
            module1,
            signal_p1_str,
            signal_n1_str + "\n",
            "\n".join(csa1_p),
            "\n".join(csa1_n),
            "\n".join(port1_out),
            "endmodule",
        ]
    )

    module2 = (
        f"module Matrix{name.upper()}{matrix_idx[name][1]}\n"
        "  import packConv::*;\n"
        "  (\n"
        f"    input  {type_input[name][1]} P,\n"
        f"    output {type_output[name][1]} soma\n"
        "  );\n"
        "  timeunit 1ns;\n"
        "  timeprecision 1ps;\n"
    )

    input2_str = np.array(
        [f"P[{i}]" for i in range(input_shp[0] * mtx.shape[1])]
    ).reshape(input_shp[0], mtx.shape[1])
    port2_pp_, port2_p = matmul_sv2(arr_p.T, input2_str)
    port2_pp = [[p for p in pp if p != 0] for pp in port2_pp_]
    signal_p2_str = (
        "  logic_vector "
        + ", ".join(f"sp{i}" for i in range(len(port2_p)))
        + ";"
    )
    csa2_p = []
    for idx, (lst_port, lst_pow) in enumerate(zip(port2_p, port2_pp)):
        pack_shift = [
            port if abs(pow) == 0 else sv_bitshift(port, pow)
            for port, pow in (zip(lst_port, lst_pow))
        ]
        lst_shift = [unpack for pack in pack_shift for unpack in pack]
        if len(lst_shift) == 0:
            pass
        elif len(lst_shift) == 1:
            csa2_p.append(f"  assign sp{idx} = {lst_shift[0]};")
        else:
            str_port = ", ".join(lst_shift)
            csa2_p.append(
                f"  CSA_{len(lst_shift)} csa_p{idx}({str_port}, sp{idx});"
            )
    port2_np_, port2_n = matmul_sv2(arr_n.T, input2_str)
    port2_np = [[p for p in pp if p != 0] for pp in port2_np_]
    signal_n2_str = (
        "  logic_vector "
        + ", ".join(f"sn{i}" for i in range(len(port2_n)))
        + ";"
    )

    csa2_n = []
    # _recursive_log2(9)
    for idx, (lst_port, lst_pow) in enumerate(zip(port2_n, port2_np)):
        pack_shift = [
            port if abs(pow) == 0 else sv_bitshift(port, pow)
            for port, pow in (zip(lst_port, lst_pow))
        ]
        lst_shift = [unpack for pack in pack_shift for unpack in pack]
        if len(lst_shift) == 0:
            pass
        elif len(lst_shift) == 1:
            csa2_n.append(f"  assign sn{idx} = {lst_shift[0]};")
        else:
            str_port = ", ".join(lst_shift)
            csa2_n.append(
                f"  CSA_{len(lst_shift)} csa_n{idx}({str_port}, sn{idx});"
            )

    port2_out = []
    for idx, (n, p) in enumerate(zip(port2_n, port2_p)):
        if len(p) > 0 and len(n) > 0:
            port2_out.append(f"  assign soma[{idx}] = sp{idx} - sn{idx};")
        elif len(p) > 0:
            port2_out.append(f"  assign soma[{idx}] = sp{idx};")
        elif len(n) > 0:
            port2_out.append(f"  assign soma[{idx}] = sn{idx};")

    m2_str = "\n".join(
        [
            module2,
            signal_p2_str,
            signal_n2_str + "\n",
            "\n".join(csa2_p),
            "\n".join(csa2_n),
            "\n".join(port2_out),
            "endmodule",
        ]
    )
    return (m1_str, m2_str)
    # breakpoint()
    # if name == "c":
    #     return (m1_str, m2_str)
    # else:
    #     return (m2_str, m1_str)


def sv_mux_mult(total, step):
    state_idx = [
        [e, [y for y in range(x, min(x + step, total))]]
        for e, x in enumerate(range(0, total, step))
    ]
    with open(Path(__file__).parent / "template/mux_mult_state.sv") as f:
        mux_mult_state_template = f.read()
    with open(Path(__file__).parent / "template/mux_mult_int.sv") as f:
        mux_mult_int_template = f.read()

    mult_state_list = [
        f"      {'default' if state==0 else 'MULT' + str(state)}: begin {''.join([f'idx[{e}]={idx}; ' for e, idx in enumerate(lst)])}end"
        for state, lst in state_idx
    ]
    mult_state_str = "\n".join(mult_state_list)

    mult_int_list = [
        f"      {'default' if state==0 else 'MULT' + str(state)}: begin {''.join([f'idx_out[{e}]={idx}; ' for e, idx in enumerate(lst)])}end"
        for state, lst in state_idx
    ]
    mult_int_str = "\n".join(mult_int_list)

    output = {
        "state": mux_mult_state_template.format(
            case=mult_state_str, num_mult=step, state_mult=total // step
        ),
        "int": mux_mult_int_template.format(
            case=mult_int_str, num_mult=step, state_mult=total // step
        ),
    }
    return output
