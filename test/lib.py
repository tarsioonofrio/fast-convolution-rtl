import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence, Union

from fast_convolution import cli

TEST_ROOT = Path(__file__).parent.resolve()
JSON_ROOT = TEST_ROOT / "json"

list_cmd_common = [
    "ex_rand",
    "ex_seq",
    "sim_int",
    "sim_file",
    "quant",
    "sim_normal",
]


@dataclass(frozen=True)
class RepoCase:
    repo_path: Path
    repo_opt: Sequence[str]
    commands: Mapping[str, Sequence[str]]

    @property
    def name(self) -> str:
        return self.repo_path.stem


def read_json(file: Union[Path, str]):
    with open(file, "r") as f:
        return json.load(f)


def load_common_commands() -> Mapping[str, Sequence[str]]:
    return read_json(JSON_ROOT / "cmd_common.json")


def collect_repo_cases(files: Iterable[Union[str, Path]]) -> list[RepoCase]:
    cases: list[RepoCase] = []
    for entry in files:
        stem = Path(entry).stem
        repo_path = TEST_ROOT / stem
        commands = read_json(JSON_ROOT / f"{stem}.json")
        cases.append(
            RepoCase(
                repo_path=repo_path,
                repo_opt=("-p", repo_path.as_posix()),
                commands=commands,
            )
        )
    return cases


def run(cmd: str, repo_path: Path, repo_opt: Sequence[str], cmd_dict: Mapping[str, Sequence[str]]):
    args = list(repo_opt) + list(cmd_dict[cmd])
    exit_code = cli.main(args)
    assert exit_code == 0, f"Project {repo_path.stem}, cmd {cmd}"
