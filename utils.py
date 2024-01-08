import numpy as np
import sympy as sy
from PIL import Image
from IPython.core.display_functions import display


def plot_pdf(page, crop_float=None,  dpi=200,):
    """
    (upper, lower)
    crop float value between 0 and 1
    """
    pix = page.get_pixmap(dpi=dpi)
    # mode = "RGBA" if pix.alpha else "RGB"
    mode = "RGB"
    image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
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
