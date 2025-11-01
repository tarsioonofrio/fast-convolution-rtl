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
    read_bind_if_exists,
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


@dataclass
class SimulationCore:
    output_fast: np.ndarray
    feat_list_sv: np.ndarray
    out_feat_list_sv: np.ndarray
    bg_quant: np.ndarray
    bg: np.ndarray
    count_nest: int
    count_mult: int


def run_simulation(payload: SimulationPayload, standard: bool):
    if standard:
        return sim_naive(payload)
    return sim(payload)


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
        if payload.quant_data == 0
        else np.round(np.array(bg).astype(float)).astype(int)
    )
    fast_conv = [
        [
            [
                fast.wrap_convolution(c, bg_quant[cout][cin][i], a, quant_bits)
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
    feat_list_sv = [
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
    feat_list_sv = np.array(feat_list_sv)
    out_feat_list_sv = [
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
    out_feat_list_sv = np.array(out_feat_list_sv)
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
        if payload.quant_data == 0
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
    feat_list_sv = [
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
    feat_list_sv = np.array(feat_list_sv)
    out_feat_list_sv = [
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
    out_feat_list_sv = np.array(out_feat_list_sv)
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
    )
    return run_simulation(payload, standard)


def cmd_sim_normal(
    repo, image_side, channel_in, channel_out, suffix, seed, standard
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
    quant_bits = quant_data["bits"] if "bits" in quant_data else 0
    # feat_quant = (
    #     feat_arr if len(quant_data) == 0 else feat_arr * (2**quant_bits)
    # ).astype(int)

    # wght_quant = (
    #     wght_arr if len(quant_data) == 0 else wght_arr * (2**quant_bits)
    # ).astype(int)

    output_default_quant = F.conv2d(
        torch.tensor(feat_quant),
        torch.tensor(wght_quant),
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
        metric = np.all(
            np.array(output_default) == np.array(core.output_fast)
        )
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
    for arr, name in zip(
        [feat_quant, wght_quant, core.output_fast, output_default_quant],
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
            "value": core.bg_quant.reshape(-1, core.bg_quant.shape[-1]),
        },
        {
            "name": "feat_in_quant",
            "value": feat_quant.reshape(-1, feat_quant.shape[-1]),
        },
        {
            "name": "feat_out",
            "value": core.output_fast.reshape(
                -1, core.output_fast.shape[-1]
            ),
        },
    ]
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
    feat_list_sv = core.feat_list_sv.reshape(
        -1, core.feat_list_sv.shape[-1]
    )
    out_feat_list_sv = core.out_feat_list_sv.reshape(
        -1, core.out_feat_list_sv.shape[-1]
    )
    output_fast_list_sv = core.output_fast.reshape(
        -1, core.output_fast.shape[-1]
    )

    const_data_size = (
        1
        + weight_sv.reshape(-1).shape[0]
        + np.array(feat_quant).reshape(-1).shape[0]
    )
    const_data_sv = [
        [[0]],
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
