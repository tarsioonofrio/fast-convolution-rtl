from __future__ import annotations

from .bind import cmd_build2d_bind_kron, cmd_build2d_bind_nest
from .build import (
    build1d,
    build2d,
    cmd_build_manual_factorization1d,
    cmd_build_manual_factorization2d,
    cmd_build_tolimlin_4x3,
    cmd_build_tolimlin_4x3_2d,
    cmd_build_toom_cook1d,
    cmd_build_toom_cook2d,
)
from .config import (
    default_toom_cook_points1d,
    default_toom_cook_points2d,
    header_init,
    now,
    num_points1d,
    num_points2d,
    package_clib,
    read_bind_if_exists,
    read_build_1d,
    read_build_2d,
    read_init,
    read_init_if_exists,
    read_num_points,
    read_quant_if_exists,
    write_bind,
)
from .examples import (
    cmd_example_list,
    cmd_example_random,
    cmd_example_sequential,
    example,
)
from .project import cmd_init, cmd_show
from .quant import cmd_quant_none, cmd_quant_shift
from .simulation import (
    cmd_sim_file,
    cmd_sim_int,
    cmd_sim_normal,
    sim,
    sim_naive,
)

__all__ = [
    # project
    "cmd_init",
    "cmd_show",
    # build
    "cmd_build_toom_cook1d",
    "cmd_build_manual_factorization1d",
    "cmd_build_tolimlin_4x3",
    "cmd_build_toom_cook2d",
    "cmd_build_manual_factorization2d",
    "cmd_build_tolimlin_4x3_2d",
    "build1d",
    "build2d",
    # bind
    "cmd_build2d_bind_nest",
    "cmd_build2d_bind_kron",
    # quant
    "cmd_quant_none",
    "cmd_quant_shift",
    # simulation
    "cmd_sim_file",
    "cmd_sim_int",
    "cmd_sim_normal",
    "sim",
    "sim_naive",
    # examples
    "cmd_example_random",
    "cmd_example_sequential",
    "cmd_example_list",
    "example",
    # config helpers (kept for compatibility)
    "default_toom_cook_points1d",
    "default_toom_cook_points2d",
    "header_init",
    "now",
    "num_points1d",
    "num_points2d",
    "package_clib",
    "read_bind_if_exists",
    "read_build_1d",
    "read_build_2d",
    "read_init",
    "read_init_if_exists",
    "read_num_points",
    "read_quant_if_exists",
    "write_bind",
]
