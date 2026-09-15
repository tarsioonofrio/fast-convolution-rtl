"""WinoCNN dataset export.

The accelerator consumes two *logical* tensors whose layouts are fixed by
``software/buffer.cpp`` in the WinoCNN repository:

    feature[addr],   addr = c*H*W + h*W + w            (channel-major)
    weight[(od*Cin + id)*kh*kw + ks]                   (Cout, Cin, kh, kw)

Both are signed 8-bit (the hardware reads ``char`` and widens internally).

``export_winocnn`` writes, under ``<sim>/winocnn/``:

    feature.bin   int8, Cin*H*W      (WinoCNN logical feature map)
    weight.bin    int8, Cout*Cin*kh*kw (WinoCNN logical weights)
    params.json   convolution descriptor (dims, stride, pad, scale, ...)
    README.md     layout and how to feed the WinoCNN flow

The WinoCNN side packs these into its DDR layout (``featuremap_int_to_hw`` /
``weight_int_to_merged_DDR``) via ``testbench/single_main.cpp`` (``file:`` mode)
and then exports the RTL stimulus with ``asic_scripts/bin2hex.py``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np


def _to_int8(array: np.ndarray) -> np.ndarray:
    """Flatten to signed 8-bit, matching the WinoCNN ``char`` buffers."""
    flat = np.asarray(array).reshape(-1).astype(np.int64)
    return np.clip(flat, -128, 127).astype(np.int8)


def export_winocnn(
    path: Path,
    feature: np.ndarray,
    weight: np.ndarray,
    channel_in: int,
    channel_out: int,
    image_side: int,
    kernel_h: int,
    kernel_w: int,
    stride: int = 1,
    pad_h: int = 0,
    pad_w: int = 0,
    relu: int = 0,
    scale: int = 128,
    bias: Optional[np.ndarray] = None,
) -> Path:
    """Write a WinoCNN-compatible logical dataset under ``path``.

    ``feature`` has shape (1, Cin, H, W) and ``weight`` (Cout, Cin, kh, kw),
    exactly as produced by the fast-convolution simulation.
    """
    feature = np.asarray(feature)
    weight = np.asarray(weight)
    if feature.ndim != 4 or weight.ndim != 4:
        raise ValueError("feature must be (1,Cin,H,W) and weight (Cout,Cin,kh,kw)")

    out_height = image_side - kernel_h + 1
    out_width = image_side - kernel_w + 1

    path.mkdir(parents=True, exist_ok=True)
    feature_i8 = _to_int8(feature)
    weight_i8 = _to_int8(weight)
    feature_i8.tofile(path / "feature.bin")
    weight_i8.tofile(path / "weight.bin")

    params = {
        "input_height": int(image_side),
        "input_width": int(image_side),
        "input_depth": int(channel_in),
        "output_height": int(out_height),
        "output_width": int(out_width),
        "output_depth": int(channel_out),
        "kernel_size_h": int(kernel_h),
        "kernel_size_w": int(kernel_w),
        "stride": int(stride),
        "pad_size_h": int(pad_h),
        "pad_size_w": int(pad_w),
        "relu": int(relu),
        "scale": int(scale),
        "feature_layout": "feature[c*H*W + h*W + w], int8",
        "weight_layout": "weight[(od*Cin + id)*kh*kw + ks], int8",
    }
    with open(path / "params.json", "w") as f:
        json.dump(params, f, indent=2)

    if bias is not None:
        _to_int8(bias).tofile(path / "bias.bin")

    (path / "README.md").write_text(
        "# WinoCNN dataset\n\n"
        "Gerado pela lib `fast-convolution-rtl`.\n\n"
        "| arquivo | conteudo |\n|---|---|\n"
        "| `feature.bin` | int8, `Cin*H*W`, layout `c*H*W + h*W + w` |\n"
        "| `weight.bin` | int8, `Cout*Cin*kh*kw`, layout `(od*Cin+id)*kh*kw + ks` |\n"
        "| `params.json` | descritor da convolucao (dims, stride, pad, scale) |\n\n"
        "Como alimentar o WinoCNN:\n\n"
        "```\n"
        "# 1) empacotar no layout DDR e validar contra o golden do WinoCNN\n"
        "testbench/single_main ... file:<dir>/feature.bin ... file:<dir>/weight.bin ...\n"
        "# 2) gerar o estimulo RTL\n"
        "python3 asic_scripts/bin2hex.py <dir>\n"
        "```\n"
    )
    return path
