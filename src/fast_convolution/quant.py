from __future__ import annotations

import json

from .repo import Repo


def cmd_quant_none(repo: Repo):
    repo.file_quant.unlink(missing_ok=True)


def cmd_quant_shift(repo: Repo, bits):
    data = {"bits": bits}
    with open(repo.file_quant, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
