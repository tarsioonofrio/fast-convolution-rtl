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
    file_list = config.getoption("--file")
