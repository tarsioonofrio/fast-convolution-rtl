from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import sympy as sy

from . import utils
from .repo import Repo


def package_clib() -> Path:
    return Path(__file__).resolve().parent / "clib"


def read_init(repo: Repo) -> Tuple[int, Any, Any, Any]:
    with open(repo.file_init) as f:
        data = json.load(f)
    c = data["c"]
    a = data["a"]
    b = data["b"]
    dim = data["dim"]
    return dim, c, b, a


def read_build_1d(repo: Repo) -> Tuple[List[int], sy.Matrix, sy.Matrix, sy.Matrix, sy.Matrix]:
    with open(repo.file_build) as f:
        data = json.load(f)
    p = data["p"]
    c = sy.Matrix(data["c"])
    b = sy.Matrix(data["b"])
    a = sy.Matrix(data["a"])
    q = sy.Matrix([sy.Rational(p, q) for p, q in data["q"]])
    return p, c, b, a, q


def read_build_2d(
    repo: Repo,
) -> Tuple[Tuple[sy.Matrix, sy.Matrix], Tuple[sy.Matrix, sy.Matrix], Tuple[sy.Matrix, sy.Matrix], Tuple[sy.Matrix, sy.Matrix], List[sy.Matrix]]:
    with open(repo.file_build) as f:
        data = json.load(f)
    p = sy.Matrix(data["p"][0]), sy.Matrix(data["p"][1])
    c = sy.Matrix(data["c"][0]), sy.Matrix(data["c"][1])
    b = sy.Matrix(data["b"][0]), sy.Matrix(data["b"][1])
    a = sy.Matrix(data["a"][0]), sy.Matrix(data["a"][1])
    q = [sy.Matrix([sy.Rational(p, q) for p, q in d]) for d in data["q"]]
    return p, c, b, a, q


def read_init_if_exists(repo: Repo) -> Dict[str, Any]:
    if repo.file_init.exists() is False:
        return {}
    with open(repo.file_init) as f:
        data = json.load(f)
    return data


def read_num_points(repo: Repo) -> Any:
    if repo.file_init.exists() is False:
        return 1
    dim, c, b, a = read_init(repo)
    return c


def num_points1d(size: Any) -> int:
    if isinstance(size, int):
        return size
    return 1


def num_points2d(size: Any, axis: int) -> int:
    if isinstance(size, list) is False:
        return 1
    return size[axis]


def default_toom_cook_points1d(size: Any):
    if isinstance(size, int) is False:
        return 1
    p0 = [p * s for s in range(1, size // 2 + size % 2) for p in [1, -1]]
    p = [0] + p0[: size - 1 - size % 2] + ["inf"]
    return p


def default_toom_cook_points2d(size0: Any, axis: int | None = None):
    if isinstance(size0, list) is False:
        return 1
    if axis is None:
        raise ValueError("axis must be provided for 2D default points")
    size = size0[axis]
    p0 = [p * s for s in range(1, size // 2 + size % 2) for p in [1, -1]]
    p = [0] + p0[: size - 1 - size % 2] + ["inf"]
    return p


def read_quant_if_exists(repo: Repo) -> Dict[str, Any]:
    if repo.file_quant.exists() is False:
        return {}
    with open(repo.file_quant) as f:
        data = json.load(f)
    return data


def now() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M")


def write_bind(repo: Repo, func: str, params=None) -> None:
    data = {"func": func, "params": params}
    with open(repo.file_bind, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def read_bind_if_exists(repo: Repo) -> Dict[str, Any]:
    if repo.file_bind.exists() is False:
        return {}
    with open(repo.file_bind) as f:
        data = json.load(f)
    return data


def dict_dimension(dim, a, b, c, m) -> Dict[str, int]:
    if dim == 1:
        dict_defs = {
            "A_SIZE": a,
            "B_SIZE": b,
            "C_SIZE": c,
            "M_SIZE": m,
        }
    else:
        dict_defs = {
            "A1_SIZE": a,
            "B1_SIZE": b,
            "C1_SIZE": c,
            "M1_SIZE": m,
            "A2_SIZE": a,
            "B2_SIZE": b,
            "C2_SIZE": c,
            "M2_SIZE": m,
        }
    return dict_defs


def header_init(repo: Repo, dimensions, a, b, c, m) -> None:
    repo.dir_clib_data.mkdir(parents=True, exist_ok=True)
    init_path = repo.dir_clib_data / "init.h"
    dict_defs = dict_dimension(dimensions, a, b, c, m)
    utils.c_header(init_path, [], dict_defs)
