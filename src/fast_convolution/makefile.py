from pathlib import Path


def makefile(target, opt, source="", include=""):
    root = Path(__file__).parent.resolve()
    with open(root / "template/makefile") as f:
        makefile_template = f.read()

    makefile_str = makefile_template.format(target=target, opt=opt,source=source, include=include)
    return makefile_str
