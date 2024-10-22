from pathlib import Path

# Variável global para armazenar a lista de arquivos
file_list = []


def pytest_addoption(parser):
    parser.addoption(
        "--file",
        action="store",
        nargs="+",  # Aceita múltiplos valores
        help="List of files to be processed",
    )


def pytest_configure(config):
    global file_list
    tmp = config.getoption("--file")
    if tmp is not None:
        file_list = tmp
    else:
        root = Path(__file__).parent.resolve()
        file_list = root.glob("json/1d*.json")
