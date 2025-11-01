from __future__ import annotations

from typing import Optional, Sequence, Tuple

from PIL import Image, ImageOps


def _validate_crop_bounds(bounds: Sequence[float]) -> Tuple[float, float]:
    if len(bounds) != 2:
        raise ValueError("crop_float must contain exactly two values (upper, lower).")
    upper, lower = bounds
    if not 0 <= upper <= 1 or not 0 <= lower <= 1:
        raise ValueError("crop_float entries must be in the range [0, 1].")
    return float(upper), float(lower)


def _render_pdf_page(page, dpi: int) -> Tuple[Image.Image, int, int]:
    pix = page.get_pixmap(dpi=dpi)
    mode = "RGB"
    image = ImageOps.invert(
        Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    )
    return image, pix.width, pix.height


def _display_image(image: Image.Image, crop_box: Optional[Tuple[int, int, int, int]]) -> None:
    from IPython.core.display_functions import display

    if crop_box is None:
        display(image)
    else:
        display(image.crop(crop_box))


def plot_pdf(page, crop_float: Optional[Sequence[float]] = None, dpi: int = 200) -> None:
    """
    Display a rendered PDF page optionally cropped by the supplied (upper, lower) bounds.
    """
    image, width, height = _render_pdf_page(page, dpi)
    crop_box = None
    if crop_float is not None:
        upper, lower = _validate_crop_bounds(crop_float)
        crop_box = (0, int(height * upper), width, int(height * lower))
    _display_image(image, crop_box)


def plot_pdf2col(
    page,
    column: int,
    crop_float: Optional[Sequence[float]] = None,
    dpi: int = 200,
) -> None:
    """
    Display a two-column PDF page, selecting a specific column and crop bounds.
    """
    if column not in (0, 1):
        raise ValueError("column must be 0 (left) or 1 (right).")

    image, width, height = _render_pdf_page(page, dpi)
    column_width = width // 2
    left = column_width * column
    right = left + column_width

    crop_box = (left, 0, right, height)
    if crop_float is not None:
        upper, lower = _validate_crop_bounds(crop_float)
        crop_box = (left, int(height * upper), right, int(height * lower))
    _display_image(image, crop_box)
