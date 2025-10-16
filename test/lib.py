import json

from click.testing import CliRunner

from fast_convolution import cli

list_cmd_common = [
    "ex_rand",
    "ex_seq",
    "sim_int",
    "sim_file",
    "quant",
    "sim_normal",
]


def run(cmd, repo_path, repo_opt, cmd_dict):
    runner = CliRunner()
    result = runner.invoke(cli.main, repo_opt + cmd_dict[cmd])
    assert result.exit_code == 0, f"Project {repo_path.stem}, cmd {cmd}"


def read_json(file):
    with open(file, "r") as f:
        return json.load(f)
