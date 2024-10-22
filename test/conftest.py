from pathlib import Path

# Variável global para armazenar a lista de arquivos
file_list1d = []
file_list2d = []


def pytest_addoption(parser):
    parser.addoption(
        "--file",
        action="store",
        nargs="+",  # Aceita múltiplos valores
        help="List of files to be processed",
    )


def pytest_configure(config):
    global file_list1d
    global file_list2d
    tmp = config.getoption("--file")
    print(tmp)
    if tmp is not None:
        file_list1d = tmp
        file_list2d = tmp
    else:
        root = Path(__file__).parent.resolve()
        file_list1d = root.glob("json/1d*.json")
        file_list2d = root.glob("json/2d*.json")
