from __future__ import annotations

import os
from pathlib import Path
from typing import Union


class Repo:
    """Represents the fast_convolution repository layout."""

    def __init__(
        self,
        path: Union[str, os.PathLike[str], None] = None,
        debug: bool = False,
    ) -> None:
        self.root = Path(os.path.abspath(path or "."))
        self.debug = debug
        self.dir_config = self.root / "config"
        self.file_init = self.dir_config / "init.json"
        self.file_build = self.dir_config / "build.json"
        self.file_gen = self.dir_config / "gen.json"
        self.file_bind = self.dir_config / "bind.json"
        self.file_quant = self.dir_config / "quant.json"
        self.dir_build = self.root / "build"
        self.dir_quant = self.root / "quant"
        self.dir_example = self.root / "example"
        self.dir_sim = self.root / "sim"
        self.dir_clib = self.root / "clib"
        self.dir_sv = self.root / "sv"
        self.dir_clib_make = self.dir_clib / "make"
        self.dir_clib_lib = self.dir_clib / "lib"
        self.dir_clib_main = self.dir_clib / "main"
        self.dir_clib_data = self.dir_clib / "data"
        self.dir_clib_data_float = self.dir_clib / "data_float"
