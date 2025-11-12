from __future__ import annotations

import json
import shutil

from .config import (
    package_clib,
    read_build_1d,
    read_build_2d,
    read_init_if_exists,
    read_quant_if_exists,
)
from .repo import Repo


def cmd_init(repo: Repo, dimensions, in_len, out_len, w):
    if repo.file_init.exists():
        return "init.json existis, fconv model already initialized"
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

    repo.dir_clib.mkdir(parents=True, exist_ok=True)
    dir_clib_x86 = repo.dir_clib / "cmake-gcc"
    shutil.copytree(
        package_clib() / "cmake-gcc", dir_clib_x86, dirs_exist_ok=True
    )
    dir_clib_common = repo.dir_clib / "common"
    shutil.copytree(
        package_clib() / "common", dir_clib_common, dirs_exist_ok=True
    )
    shutil.copytree(
        package_clib() / "src/int/lib", repo.dir_clib_lib, dirs_exist_ok=True
    )


def cmd_show(repo: Repo, init, build, quant_):
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
    return None
