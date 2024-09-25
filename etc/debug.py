import importlib
from pathlib import Path

repo_name = "1d3"
function_name = "test_build"

root = Path(__file__).parent.parent.resolve() / "test"
file_path = root / f"{repo_name}.py"
repo_path = root / repo_name
repo_opt = ["-p", repo_path.as_posix()]

# Cria um spec de importação baseado no caminho do arquivo
spec = importlib.util.spec_from_file_location(repo_name, file_path)
module = importlib.util.module_from_spec(spec)

# Carrega o módulo
spec.loader.exec_module(module)

# Retorna a função importada
function = getattr(module, function_name)

output = function()

print(output)

