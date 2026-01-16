from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
from PIL import Image
from scipy import signal
from sklearn.metrics import r2_score

from . import fast, utils
from .config import (
    read_build_1d,
    read_build_2d,
    read_init,
    read_quant_if_exists,
)
from .naive import naive_convolve
from .repo import Repo


@dataclass
class SimulationPayload:
    repo: Repo
    dim: int
    a_len: Any
    b_len: Any
    c_len: Any
    feature: np.ndarray
    feature_quant: np.ndarray
    feature_info: Optional[str]
    image_side: int
    quant_data: dict
    suffix: str
    weight_info: Optional[str]
    weight: np.ndarray
    weight_quant: np.ndarray
    channel_in: int
    channel_out: int
    bias: Optional[np.ndarray] = None
    bias_quant: Optional[np.ndarray] = None


@dataclass
class SimulationCore:
    output_fast: np.ndarray
    feat_list_sv: np.ndarray
    out_feat_list_sv: np.ndarray
    bg_quant: np.ndarray
    bg: np.ndarray
    count_nest: int
    count_mult: int


def _reshape_bias(bias: np.ndarray, target: np.ndarray) -> np.ndarray:
    if bias.ndim != 1:
        raise ValueError("Bias must be a 1D array.")
    shape = (bias.shape[0],) + (1,) * (target.ndim - 1)
    return bias.reshape(shape)


def _apply_bias(output: np.ndarray, bias: Optional[np.ndarray]) -> np.ndarray:
    if bias is None:
        return output
    return output + _reshape_bias(bias, output)


def _quantize_bias(
    bias: Optional[np.ndarray], quant_bits: int, has_quant: bool
) -> Optional[np.ndarray]:
    if bias is None:
        return None
    if has_quant:
        return np.round(bias * (2**quant_bits)).astype(int)
    return bias.astype(int)


def run_simulation(payload: SimulationPayload, standard: bool):
    if standard:
        return sim_naive(payload)
    return sim(payload)


def _compute_bg_1d(
    wght_quant: np.ndarray,
    q,
    b,
    channel_out: int,
    channel_in: int,
    length: int,
):
    return np.array(
        [
            [
                [
                    fast.g_to_bg(q, b, wght_quant[cout][cin][i]).T
                    for i in range(length)
                ]
                for cin in range(channel_in)
            ]
            for cout in range(channel_out)
        ]
    )


def _fast_convolutions_1d(
    bg_quant, channel_out, channel_in, b_len, c, a, quant
):
    return [
        [
            [
                fast.wrap_convolution(c, bg_quant[cout][cin][i], a, quant)
                for i in range(b_len)
            ]
            for cin in range(channel_in)
        ]
        for cout in range(channel_out)
    ]


def _collect_windows_1d(payload, output_fast, output_shape):
    channel_in = payload.channel_in
    channel_out = payload.channel_out
    feat_windows = [
        fast.sliding1d_window2d(
            payload.feature_quant[0][cin],
            output_fast[0],
            output_shape,
            payload.c_len,
            payload.a_len,
            False,
        )
        for cin in range(channel_in)
    ]
    out_windows = [
        fast.sliding1d_window2d(
            payload.feature_quant[0][0],
            output_fast[cout],
            output_shape,
            payload.c_len,
            payload.a_len,
            True,
        )
        for cout in range(channel_out)
    ]
    return np.array(feat_windows), np.array(out_windows)


def _compute_bg_2d(wght_quant, q, b, channel_out, channel_in):
    return np.array(
        [
            [
                fast.g_to_bg2d(q[0], b[0], q[1], b[1], wght_quant[cout, cin])
                for cin in range(channel_in)
            ]
            for cout in range(channel_out)
        ]
    )


def _fast_convolutions_2d(bg_quant, channel_out, channel_in, c, a, quant):
    return [
        [
            fast.wrap_convolution2d(
                c[0], c[1], bg_quant[cout][cin], a[0], a[1], quant
            )
            for cin in range(channel_in)
        ]
        for cout in range(channel_out)
    ]


def _collect_windows_2d(payload, output_fast, output_shape):
    channel_in = payload.channel_in
    channel_out = payload.channel_out
    feat_windows = [
        fast.sliding2d_window2d(
            payload.feature_quant[0][cin],
            output_fast[0],
            output_shape,
            payload.c_len,
            payload.a_len,
            False,
        )
        for cin in range(channel_in)
    ]
    out_windows = [
        fast.sliding2d_window2d(
            payload.feature_quant[0][0],
            output_fast[cout],
            output_shape,
            payload.c_len,
            payload.a_len,
            True,
        )
        for cout in range(channel_out)
    ]
    return np.array(feat_windows), np.array(out_windows)


def _save_arrays(base_path, entries, fmt):
    for name, array in entries:
        np.savetxt(base_path / f"{name}.txt", array, fmt=fmt)


def _save_flat_arrays(base_path, entries, fmt):
    for name, array in entries:
        flat = np.array(array).reshape(-1)
        np.savetxt(base_path / f"{name}.txt", flat, fmt=fmt)


def _prepend_bias(values: np.ndarray, bias: Optional[np.ndarray]) -> np.ndarray:
    if bias is None:
        return np.array(values)
    return np.concatenate(
        [np.array(bias).reshape(-1), np.array(values).reshape(-1)]
    )


def _bias_or_zeros(
    bias: Optional[np.ndarray],
    channel_out: int,
    dtype: np.dtype,
) -> np.ndarray:
    if bias is None:
        return np.zeros(channel_out, dtype=dtype)
    return np.array(bias).astype(dtype, copy=False)


def _flatten_last_axis(arr: np.ndarray) -> np.ndarray:
    arr_np = np.array(arr)
    return arr_np.reshape(-1, arr_np.shape[-1])


def _simulate_1d_core(
    payload: SimulationPayload,
    wght_quant: np.ndarray,
    output_shape,
    quant_bits: int,
) -> SimulationCore:
    repo = payload.repo
    channel_in = payload.channel_in
    channel_out = payload.channel_out
    b_len = int(payload.b_len)
    points, c, b, a, q = read_build_1d(repo)
    bg = _compute_bg_1d(wght_quant, q, b, channel_out, channel_in, b_len)
    bg_quant = (
        bg
        if payload.quant_data == 0
        else np.round(np.array(bg).astype(float)).astype(int)
    )
    fast_conv = _fast_convolutions_1d(
        bg_quant, channel_out, channel_in, b_len, c, a, quant_bits
    )

    output_fast_ = [
        [
            [
                fast.filter1d_slide2d(
                    fast_conv[cout][cin][i],
                    payload.feature_quant[0][cin],
                    output_shape,
                    i,
                    payload.c_len,
                    payload.a_len,
                )
                for i in range(b_len)
            ]
            for cin in range(channel_in)
        ]
        for cout in range(channel_out)
    ]
    output_fast = np.sum(axis=(1, 2), a=output_fast_)
    bias_fast = (
        payload.bias_quant if len(payload.quant_data) != 0 else payload.bias
    )
    output_fast = _apply_bias(output_fast, bias_fast)
    feat_list_sv, out_feat_list_sv = _collect_windows_1d(
        payload, output_fast, output_shape
    )
    count_nest = np.prod(out_feat_list_sv.shape[:-1])
    count_mult = int(count_nest * len(q) * b_len)
    return SimulationCore(
        output_fast=output_fast,
        feat_list_sv=feat_list_sv,
        out_feat_list_sv=out_feat_list_sv,
        bg_quant=bg_quant,
        bg=bg,
        count_nest=count_nest,
        count_mult=count_mult,
    )


def _simulate_2d_core(
    payload: SimulationPayload,
    wght_quant: np.ndarray,
    output_shape,
    quant_bits: int,
) -> SimulationCore:
    repo = payload.repo
    channel_in = payload.channel_in
    channel_out = payload.channel_out
    points, c, b, a, q = read_build_2d(repo)
    bg = _compute_bg_2d(wght_quant, q, b, channel_out, channel_in)
    bg_quant = (
        bg
        if payload.quant_data == 0
        else np.round(np.array(bg).astype(float)).astype(int)
    )
    fast_conv = _fast_convolutions_2d(
        bg_quant, channel_out, channel_in, c, a, quant_bits
    )

    output_fast_ = np.array(
        [
            [
                fast.filter2d_slide2d(
                    fast_conv[cout][cin],
                    payload.feature_quant[0][cin],
                    output_shape,
                    payload.c_len,
                    payload.a_len,
                )
                for cin in range(channel_in)
            ]
            for cout in range(channel_out)
        ]
    )
    output_fast = np.sum(output_fast_, axis=1)
    bias_fast = (
        payload.bias_quant if len(payload.quant_data) != 0 else payload.bias
    )
    output_fast = _apply_bias(output_fast, bias_fast)
    feat_list_sv, out_feat_list_sv = _collect_windows_2d(
        payload, output_fast, output_shape
    )
    count_nest = np.prod(out_feat_list_sv.shape[:-1])
    count_mult = int(
        count_nest
        * np.prod(
            [np.prod(np.array(q[0]).shape), np.prod(np.array(q[1]).shape)]
        )
    )
    return SimulationCore(
        output_fast=output_fast,
        feat_list_sv=feat_list_sv,
        out_feat_list_sv=out_feat_list_sv,
        bg_quant=bg_quant,
        bg=bg,
        count_nest=count_nest,
        count_mult=count_mult,
    )


def _simulate_core(
    payload: SimulationPayload,
    wght_quant: np.ndarray,
    output_shape,
    quant_bits: int,
) -> SimulationCore:
    if payload.dim == 1:
        return _simulate_1d_core(payload, wght_quant, output_shape, quant_bits)
    return _simulate_2d_core(payload, wght_quant, output_shape, quant_bits)


def cmd_sim_file(repo, feature_info, weight, suffix, bias_value, standard):
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
    bias = None
    bias_quant = None
    if bias_value is not None:
        channel_out = int(wght_arr.shape[0])
        bias = np.arange(bias_value, bias_value + channel_out).astype(int)
        quant_bits = quant_data["bits"] if "bits" in quant_data else 0
        bias_quant = _quantize_bias(
            bias, quant_bits, has_quant=len(quant_data) > 0
        )
    payload = SimulationPayload(
        repo=repo,
        dim=dim,
        a_len=a_len,
        b_len=b_len,
        c_len=c_len,
        feature=feat_arr,
        feature_quant=feat_arr,
        feature_info=str(feature_info) if feature_info is not None else None,
        image_side=image_side,
        quant_data=quant_data,
        suffix=suffix,
        weight_info=str(weight) if weight is not None else None,
        weight=wght_arr,
        weight_quant=wght_arr,
        channel_in=int(feat_arr.shape[1]),
        channel_out=int(wght_arr.shape[0]),
        bias=bias,
        bias_quant=bias_quant,
    )
    return run_simulation(payload, standard)


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
    bias_value,
    standard,
):
    dim, c_len, b_len, a_len = read_init(repo)
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
            feature_info + image_side**2,
        )
        feat_arr = feat.reshape(1, 1, image_side, image_side).repeat(
            channel_in, axis=1
        )

    w_len = b_len if dim == 1 else b_len[0]
    if random:
        wght_arr = np.random.randint(
            weight,
            weight + channel_out * channel_in * w_len**2,
            size=(channel_out, channel_in, w_len, w_len),
        )
    else:
        wght = np.arange(weight, weight + w_len**2)
        wght_arr = (
            wght.reshape(1, 1, w_len, w_len)
            .repeat(channel_out, axis=0)
            .repeat(channel_in, axis=1)
        )

    quant_data = read_quant_if_exists(repo)
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    wght_quant = (
        wght_arr if len(quant_data) == 0 else wght_arr * (2**quant_bits)
    ).astype(int)
    bias = None
    bias_quant = None
    if bias_value is not None:
        if random:
            high = bias_value + max(channel_out, 1)
            bias = np.random.randint(
                bias_value, high, size=(channel_out,)
            ).astype(int)
        else:
            bias = np.arange(bias_value, bias_value + channel_out).astype(int)
        bias_quant = _quantize_bias(
            bias, quant_bits, has_quant=len(quant_data) > 0
        )
    payload = SimulationPayload(
        repo=repo,
        dim=dim,
        a_len=a_len,
        b_len=b_len,
        c_len=c_len,
        feature=feat_arr,
        feature_quant=feat_arr,
        feature_info=str(feature_info) if feature_info is not None else None,
        image_side=image_side,
        quant_data=quant_data,
        suffix=suffix,
        weight_info=str(weight) if weight is not None else None,
        weight=wght_arr,
        weight_quant=wght_quant,
        channel_in=channel_in,
        channel_out=channel_out,
        bias=bias,
        bias_quant=bias_quant,
    )
    return run_simulation(payload, standard)


def cmd_sim_normal(
    repo,
    image_side,
    channel_in,
    channel_out,
    suffix,
    seed,
    bias_mean,
    standard,
):
    dim, c_len, b_len, a_len = read_init(repo)
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

    quant_data = read_quant_if_exists(repo)
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    feat_quant = (
        feat_arr if len(quant_data) == 0 else feat_arr * (2**quant_bits)
    ).astype(int)
    wght_quant = (
        wght_arr if len(quant_data) == 0 else wght_arr * (2**quant_bits)
    ).astype(int)
    bias = None
    bias_quant = None
    if bias_mean is not None:
        bias = np.random.normal(bias_mean, 1.0, size=(channel_out,))
        bias_quant = _quantize_bias(
            bias, quant_bits, has_quant=len(quant_data) > 0
        )
    payload = SimulationPayload(
        repo=repo,
        dim=dim,
        a_len=a_len,
        b_len=b_len,
        c_len=c_len,
        feature=feat_arr,
        feature_quant=feat_quant,
        feature_info=None,
        image_side=image_side,
        quant_data=quant_data,
        suffix=suffix,
        weight_info=None,
        weight=wght_arr,
        weight_quant=wght_quant,
        channel_in=channel_in,
        channel_out=channel_out,
        bias=bias,
        bias_quant=bias_quant,
    )
    return run_simulation(payload, standard)


def sim(payload: SimulationPayload):
    a_len = payload.a_len
    b_len = payload.b_len
    c_len = payload.c_len
    dim = payload.dim
    feat_arr = payload.feature
    feat_quant = payload.feature_quant
    feature_info = payload.feature_info
    image_side = payload.image_side
    quant_data = payload.quant_data
    repo = payload.repo
    suffix = payload.suffix
    weight = payload.weight_info
    wght_arr = payload.weight
    wght_quant = payload.weight_quant
    channel_in = payload.channel_in
    channel_out = payload.channel_out
    bias = payload.bias
    bias_quant = payload.bias_quant
    import torch
    from torch import nn
    from torch.nn import functional as F

    # output_default = signal.convolve2d(
    #     feat_arr, wght_arr[::-1, ::-1], mode="valid"
    # )
    feat_tensor = torch.tensor(feat_arr)
    wght_tensor = torch.tensor(wght_arr)
    bias_tensor = None
    if bias is not None:
        bias_tensor = torch.tensor(bias).to(wght_tensor.dtype)
    output_default = F.conv2d(
        feat_tensor,
        wght_tensor,
        bias=bias_tensor,
        stride=1,
    )
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    # feat_quant = (
    #     feat_arr if len(quant_data) == 0 else feat_arr * (2**quant_bits)
    # ).astype(int)

    # wght_quant = (
    #     wght_arr if len(quant_data) == 0 else wght_arr * (2**quant_bits)
    # ).astype(int)

    feat_quant_tensor = torch.tensor(feat_quant)
    wght_quant_tensor = torch.tensor(wght_quant)
    bias_quant_tensor = None
    if bias_quant is not None:
        bias_quant_tensor = torch.tensor(bias_quant).to(
            wght_quant_tensor.dtype
        )
    output_default_quant = F.conv2d(
        feat_quant_tensor,
        wght_quant_tensor,
        bias=bias_quant_tensor,
        stride=1,
    )
    output_shape = [output_default.shape[-1], output_default.shape[-2]]
    core = _simulate_core(payload, wght_quant, output_shape, quant_bits)

    if len(quant_data) != 0:
        metric = r2_score(
            output_default.reshape(-1),
            np.array(core.output_fast).reshape(-1) / (2**quant_bits),
        )
        text_metric = f"R2: {metric}\n"
    else:
        metric = np.all(np.array(output_default) == np.array(core.output_fast))
        text_metric = f"Output default and fast are equals: {metric}\n"

    size = np.prod(output_default.shape)
    text = (
        f"Feature: {feature_info}\n"
        f"Weights: {weight}\n"
        f"Bias enabled: {bias is not None}\n"
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
        f"Convolutions: {core.count_nest}\n"
        f"Multiplications: {core.count_mult}\n"
    )
    if len(suffix) > 0:
        path = repo.dir_sim / f"sim-{suffix}"
    else:
        path = repo.dir_sim / "sim"
    path.mkdir(exist_ok=True, parents=True)
    with open(path / "sim.txt", "w") as f:
        f.write(text)
    bias_dense = _bias_or_zeros(bias_quant, channel_out, wght_quant.dtype)
    bias_float = _bias_or_zeros(bias, channel_out, wght_arr.dtype)
    dense_exports = [
        ("d", feat_quant),
        ("g", _prepend_bias(wght_quant, bias_dense)),
        ("s", core.output_fast),
        ("s_default_quant", output_default_quant),
    ]
    if bias_quant is not None:
        dense_exports.append(("bias", bias_quant))
    _save_flat_arrays(path, dense_exports, fmt="%d")

    float_exports = [
        ("d_default", feat_arr),
        ("g_default", _prepend_bias(wght_arr, bias_float)),
        ("s_default", output_default),
    ]
    if bias is not None:
        float_exports.append(("bias_default", bias))
    _save_flat_arrays(path, float_exports, fmt="%f")

    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    list_quant = [
        {
            "name": "weight",
            "value": wght_quant.reshape(-1, wght_quant.shape[-1]),
        },
        {
            "name": "weight_gg",
            "value": core.bg_quant.reshape(-1, core.bg_quant.shape[-1]),
        },
        {
            "name": "feat_in_quant",
            "value": feat_quant.reshape(-1, feat_quant.shape[-1]),
        },
        {
            "name": "feat_out",
            "value": core.output_fast.reshape(-1, core.output_fast.shape[-1]),
        },
    ]
    if bias_quant is not None:
        list_quant.append(
            {
                "name": "bias",
                "value": bias_quant.reshape(1, -1),
            }
        )
    list_float = [
        {
            "name": "weight",
            "value": wght_arr.reshape(-1, wght_arr.shape[-1]),
        },
        {"name": "weight_gg", "value": core.bg.reshape(-1, core.bg.shape[-1])},
        {"name": "feat_in", "value": feat_arr.reshape(-1, feat_arr.shape[-1])},
        {
            "name": "feat_out",
            "value": output_default.reshape(-1, output_default.shape[-1]),
        },
    ]
    if bias is not None:
        list_float.append(
            {
                "name": "bias",
                "value": bias.reshape(1, -1),
            }
        )
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

    weight_sv = core.bg_quant.reshape(
        -1, core.bg_quant.shape[-1] * core.bg_quant.shape[-2]
    )
    feat_list_sv = core.feat_list_sv.reshape(-1, core.feat_list_sv.shape[-1])
    out_feat_list_sv = core.out_feat_list_sv.reshape(
        -1, core.out_feat_list_sv.shape[-1]
    )
    output_fast_list_sv = core.output_fast.reshape(
        -1, core.output_fast.shape[-1]
    )
    const_data_size = (
        bias_dense.reshape(-1).shape[0]
        + weight_sv.reshape(-1).shape[0]
        + np.array(feat_quant).reshape(-1).shape[0]
    )
    const_data_sv = [
        [bias_dense.reshape(-1).astype(int).tolist()],
        weight_sv.tolist(),
        feat_quant.reshape(-1, feat_quant.shape[-1]).tolist(),
    ]
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
        "FEAT_OUTPUT_SIZE": core.output_fast.shape[-1],
        "N_WINDOW": core.output_fast.shape[-1]
        // (a_len if dim == 1 else a_len[0]),
        "N_CHANNEL_IN": channel_in,
        "N_CHANNEL_OUT": channel_out,
    }
    utils.sv_pkg("pack_data", path / "pack_data.sv", list1d, arr, dict_def)
    return out_dict


def sim_naive(payload: SimulationPayload):
    a_len = payload.a_len
    b_len = payload.b_len
    c_len = payload.c_len
    dim = payload.dim
    feat_arr = payload.feature
    feature_info = payload.feature_info
    image_side = payload.image_side
    quant_data = payload.quant_data
    repo = payload.repo
    suffix = payload.suffix
    weight = payload.weight_info
    wght_arr = payload.weight
    bias = payload.bias
    output_default = signal.convolve2d(
        feat_arr, wght_arr[::-1, ::-1], mode="valid"
    )
    output_default = _apply_bias(output_default, bias)
    output_naive = _apply_bias(naive_convolve(feat_arr, wght_arr), bias)
    compare_naive = np.all(output_default == output_naive)
    text_equal = f"Output default and naive are equals: {compare_naive}\n"
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    wght_quant = (
        wght_arr
        if len(quant_data) == 0
        else np.left_shift(wght_arr, quant_bits)
    )
    bias_quant = payload.bias_quant
    bias_dense = _bias_or_zeros(
        bias_quant, payload.channel_out, wght_quant.dtype
    )

    output_quant = np.right_shift(
        naive_convolve(feat_arr, wght_quant), quant_bits
    )
    bias_quant = (
        payload.bias_quant if len(quant_data) != 0 else payload.bias
    )
    output_quant = _apply_bias(output_quant, bias_quant)
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
    _save_flat_arrays(
        path,
        [
            ("d", feat_arr),
            ("g", _prepend_bias(wght_quant, bias_dense)),
            ("s_default", output_default),
            ("s", output_quant),
        ],
        fmt="%d",
    )
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
