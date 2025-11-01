from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from .bitmath import log2_lst, matrix_to_log2

CarrySaveConfig = Dict[Tuple[str, str], int]


def count_sums(matrix) -> int:
    decomposed = matrix_to_log2(matrix)
    counts = [
        [1 if -1 in term.args else len(term.args) for term in row]
        for row in decomposed.tolist()
    ]
    return int(np.sum(counts))


def max_power(entries, positive: bool = True) -> int:
    signal = 1 if positive else -1
    return max(
        [0]
        + [
            max(
                [0]
                + [
                    max(item["z"])
                    for item in row
                    if item and item.get("s") == signal and "z" in item
                ]
            )
            for row in entries
        ]
    )


def csa_lst(matrix, positive: bool = True):
    entries = log2_lst(matrix)
    signal = 1 if positive else -1
    power = max_power(entries, positive)
    return [
        [
            [
                1
                if cell
                and cell.get("s") == signal
                and "z" in cell
                and power_idx in cell["z"]
                else 0
                for cell in row
            ]
            for row in entries
        ]
        for power_idx in range(power + 1)
    ]


def csa_config(a, c) -> CarrySaveConfig:
    return {
        (name, suffix): max_power(log2_lst(matrix), positive=is_positive)
        for matrix, name in zip([a.T, c.T], ["a", "c"])
        for is_positive, suffix in zip([True, False], ["p", "n"])
    }


def csa_config_nest(a1, a2, c1, c2) -> CarrySaveConfig:
    return {
        (name, suffix): max_power(log2_lst(matrix), positive=is_positive)
        for matrix, name in zip([a1.T, a2.T, c1.T, c2.T], ["a", "A", "c", "C"])
        for is_positive, suffix in zip([True, False], ["p", "n"])
    }


def write_csa_config(config: CarrySaveConfig, path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "config.txt", "w") as fh:
        for (name, suffix), power in config.items():
            fh.write(f"{power} {name} {suffix}\n")


def csa_parcels(a, c):
    return {
        (name, suffix): csa_lst(matrix, positive=is_positive)
        for matrix, name in zip([a.T, c.T], ["a", "c"])
        for is_positive, suffix in zip([True, False], ["p", "n"])
    }


def csa_parcels_nest(a1, a2, c1, c2):
    return {
        (name, suffix): csa_lst(matrix, positive=is_positive)
        for matrix, name in zip(
            [a1, a2.T, c1, c2.T], ["a1", "a2", "c1", "c2"]
        )
        for is_positive, suffix in zip([True, False], ["p", "n"])
    }


def write_csa_parcels(csa_map, path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

    with open(path / "info.txt", "w") as fh:
        for (name, suffix), parcel in csa_map.items():
            fh.write(f"{np.sum(parcel)} {name} {suffix}\n")

    for (name, suffix), parcel in csa_map.items():
        with open(path / f"{name}{suffix}.txt", "w") as fh:
            for power in parcel:
                for line in power:
                    fh.write(" ".join(map(str, line)) + "\n")
                fh.write("\n")
