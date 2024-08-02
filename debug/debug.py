import os
from pathlib import Path


root = Path(__file__).resolve().parent.parent
example_path = root / "images"
path1d = root.parent / "test_1d"
path2d = root.parent / "test_2d"


def cmd_build_toom_cook1d():
    from fast_convolution.commands import cmd_build_toom_cook1d
    cmd_build_toom_cook1d([0, 1, -1, 2, "inf"])


def cmd_sim_file():
    from fast_convolution.commands import cmd_sim_file
    cmd_sim_file(example_path / "karatsuba032.jpg", example_path / "laplace.json")


def main():
    cmd_sim_file()


if __name__ == '__main__':
    main()
