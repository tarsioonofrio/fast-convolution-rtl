from IPython.core.display_functions import display
from PIL import Image


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