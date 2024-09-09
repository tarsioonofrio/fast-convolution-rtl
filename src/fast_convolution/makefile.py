from pathlib import Path


def makefile(files):
    root = Path(__file__).parent.resolve()
    with open(root / "template/makefile_base") as f:
        makefile_base = f.read()
    with open(root / "template/makefile_recipes") as f:
        makefile_target = f.read()
    files_str = "\n".join([f"TARGET{e} = {n}" for e, n in enumerate(files)])
    all_str = "all:" + " ".join(
        [f"$(TARGET{e}).bin $(TARGET{e}).lst" for e, n in enumerate(files)]
    )
    targets_str = "\n".join(
        [makefile_target.format(target=e) for e, n in enumerate(files)]
    )
    makefile_str = (
        files_str + "\n" + makefile_base + "\n" + all_str + "\n" + targets_str
    )
    return makefile_str
