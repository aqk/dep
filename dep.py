#!/usr/bin/env python3
from __future__ import annotations

import dataclasses
import json
import subprocess
from enum import Enum
from pathlib import Path
from typing import Dict, List, Protocol


class FetchMethod(Enum):
    GIT = 0
    TARBALL = 1


def read_config(filename) -> List[DepDescriptor]:
    with open(Path(filename)) as file:
        config = json.load(file)
    return config


verbose = True


def vprint(s: str):
    if verbose:
        print(s)


def create_dir(absolute_path: Path):
    cmd = ["mkdir", "-p", str(absolute_path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    vprint(p.stdout)


class DepDescriptor(Protocol):
    def fetch(self) -> None:
        pass

    def update(self) -> None:
        pass

    def check(self) -> None:
        pass


@dataclasses.dataclass
class GitDependency:
    dirname: Path
    hash: str
    method: FetchMethod
    url: str

    def __init__(self, config: Dict[str, str]):
        self.root = "."
        self.expected = ["dirname", "method", "url", "hash"]
        for field, value in config.items():
            self.__setattr__(field, value)
        self.full_path = Path(self.root) / self.dirname

    def fetch(self) -> None:
        create_dir(self.full_path)
        cmds: List[List[str]] = list(
            map(
                str.split,
                f"""
            git init
            git remote add dep-head {self.url}
            git fetch --depth 1 dep-head {self.hash}
            git checkout FETCH_HEAD""".split(
                    "\n"
                ),
            )
        )

        for cmd in cmds:
            if len(cmd) > 0:
                vprint(f"{' '.join(cmd)}: ")
                p = subprocess.run(
                    cmd,
                    cwd=self.full_path,
                    stdout=subprocess.PIPE,
                    universal_newlines=True,
                )
                vprint(p.stdout)

    def update(self) -> None:
        pass

    def check(self) -> None:
        pass


def dep(filename):
    """Read a specification file for dependencies and keep them up to date"""
    config = read_config(filename)
    vprint(f"Config: {config}")

    for dep in config:
        if dep["method"] == "git":
            g = GitDependency(dep)
            vprint(str(g.__dict__))
            g.fetch()


if __name__ == "__main__":
    import sys

    dep(sys.argv[1])
