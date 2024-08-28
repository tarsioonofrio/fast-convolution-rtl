import os
from pathlib import Path

import numpy as np
import sympy as sy
from PIL import Image, ImageOps
from scipy import signal

from fast_convolution import fast


def plot_pdf(page, crop_float=None,  dpi=200,):
    """
    (upper, lower)
    crop float value between 0 and 1
    """
    from IPython.core.display_functions import display
    pix = page.get_pixmap(dpi=dpi)
    # mode = "RGBA" if pix.alpha else "RGB"
    mode = "RGB"
    image = ImageOps.invert(Image.frombytes(mode, [pix.width, pix.height], pix.samples))
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
    image = ImageOps.invert(Image.frombytes(mode, [pix.width, pix.height], pix.samples))
    if crop_float is None:
        display(image)
    else:
        assert 0 <= crop_float[0] <= 1
        assert 0 <= crop_float[1] <= 1
        assert column in [0, 1]
        left = (pix.width)//2 * column
        upper = int(pix.height * crop_float[0])
        right = (pix.width)//2 * (column + 1)
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
            args = [i for e, i in enumerate(polynomial.args) if sum([quo, rem])-1 != e]
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
    out_clip = out[size:2 * size]
    out_mtx = sy.Matrix(out_clip)
    return out_mtx


def winograd_cyclic_conv2x2(x, y):
    ax0 = x[0]+x[1]
    ax1 = x[0]-x[1]
    bx0 = (y[0]+y[1])/2
    bx1 = (y[0]-y[1])/2

    m0 = ax0*bx0
    m1 = ax1*bx1
    s0 = m0 + m1
    s1 = m0 - m1
    return (s0, s1)


# https://stackoverflow.com/a/38034801
def conv_circ_fft(signal, kernel):
    '''
        signal: real 1D array
        ker: real 1D array
        signal and ker must have same shape
    '''
    return np.real(np.fft.ifft(np.fft.fft(signal)*np.fft.fft(kern)))


def c_header(path, list_array, dict_defs):
    name = path.stem.upper()
    source_str = (
        f"#ifndef C_{name}_H\n"
        f"#define C_{name}_H\n\n"
        "{code}\n"
        f"#endif //C_{name}_H\n"
    )
    array_str = (
        "const {type} {name}[{size}] = {{\n"
        "{value}\n"
        "}};\n"
    )
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
                value_str = (",\n").join(["\t" + ", ".join(map(lambda x: str(x) + "f", v)) for v in value])
            else:
                value_str = (",\n").join(["\t" + ", ".join(map(str, v)) for v in value])
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
    mtx_log = fast.log2_lst(mtx)
    var_in = [f"m_in[{i}]" for i in range(mtx.shape[1])]
    var_out = [f"m_out[{i}]" for i in range(mtx.shape[0])]

    lst_data = [[
        [c_shift(d, num["s"], z) for z in num["z"]]
        for d, num in zip(var_in, row) if "s" in num]
        for row in mtx_log
    ]
    lst_join = [
        "".join(["".join(num) for num in row])
        for row in lst_data
    ]
    lst_output = [f"\t{m} = {d};" for m, d in zip(var_out, lst_join)]
    lst_str = "\n".join(lst_output)
    header = f"void matrix_mul_shift_noloop_{name_suffix}(int *m_out, const int *m_in)"
    function = (
        f"{header}{{\n"
        f"{lst_str}\n"
        "}\n"
    )
    return {"header": f"{header};\n", "function": function}

def c_matmul_shift_noloop_iter(mtx, name_suffix):
    mtx_log = fast.log2_lst(mtx)
    var_in = [f"m_in[{i}]" for i in range(mtx.shape[0] * mtx.shape[1])]
    var_out = [f"m_out[{i}]" for i in range(mtx.shape[0] * mtx.shape[1])]

    lst_data = [[
        [c_shift(d, num["s"], z) for z in num["z"]]
        for d, num in zip(var_in[r: r + mtx.shape[0]], row) if "s" in num]
        for r in range(0, mtx.shape[0] * mtx.shape[1], mtx.shape[0])
        for row in mtx_log
    ]
    lst_join = [
        "".join(["".join(num) for num in row])
        for row in lst_data
    ]
    lst_output = [f"\t{m} = {d};" for m, d in zip(var_out, lst_join)]
    lst_str = "\n".join(lst_output)
    header = f"void matrix_mul_shift_noloop_{name_suffix}(int *m_out, const int *m_in)"
    function = (
        f"{header}{{\n"
        f"{lst_str}\n"
        "}\n"
    )
    return {"header": f"{header};\n", "function": function}

def c_hadamart_product_nollop(size):
    lst = [f"\tout[{i}] = in1[{i}] * in2[{i}];" for i in range(size)]
    lst_str = "\n".join(lst)
    header = "void hadamart_product_noloop(int *out, const int *in1, const int *in2)"
    function = (
        f"{header}{{\n"
        f"{lst_str}\n"
        "}\n"
    )
    return {"header": f"{header};\n", "function": function}


def default_convolve(f, w):
    output_default = signal.convolve(
        f, w[::-1, ::-1], mode='valid'
    )
    return output_default


def getcwd():
    import os
    if os.environ.get("TEST_PATH") is None:
        return Path(os.getcwd())
    else:
        return Path(os.environ.get("TEST_PATH"))


root_project_path = getcwd()
dir_config = root_project_path / "config"
file_init = dir_config / "init.json"
file_build = dir_config / "build.json"
file_bind = dir_config / "bind.json"
file_quant = dir_config / "quant.json"
dir_build = root_project_path / "build"
dir_quant = root_project_path / "quant"
dir_example = root_project_path / "example"
dir_sim = root_project_path / "sim"
dir_clib_data = root_project_path / "clib/src/data"
clib_package = Path(__file__).resolve().parent / "clib"
