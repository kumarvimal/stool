from __future__ import annotations

import subprocess
from pathlib import Path

DEFAULT_BRANCH_COUNT = 4


def _latest_branches(number: int) -> str:
    if number < 1:
        raise ValueError("number must be greater than 0")

    result = subprocess.run(
        [
            "git",
            "for-each-ref",
            f"--count={number}",
            "--sort=-committerdate",
            "--format=%(committerdate:relative)%09%(refname:short)",
            "refs/heads",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _git_stdout(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo_root() -> Path:
    return Path(_git_stdout("rev-parse", "--show-toplevel"))


def _branch_exists(branch: str) -> bool:
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        check=False,
    )
    return result.returncode == 0


def _validate_branch(branch: str) -> None:
    subprocess.run(["git", "check-ref-format", "--branch", branch], check=True)


def _worktrees() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    entry: dict[str, str] = {}
    for line in _git_stdout("worktree", "list", "--porcelain").splitlines():
        if not line:
            entries.append(entry)
            entry = {}
            continue
        key, _, value = line.partition(" ")
        entry[key] = value
    if entry:
        entries.append(entry)
    return entries


def _list_worktrees() -> str:
    lines = []
    for entry in _worktrees():
        branch = entry.get("branch", "detached").removeprefix("refs/heads/")
        path = entry["worktree"]
        lines.append(f"{branch}\t{path}")
    return "\n".join(lines) + "\n"


def _linked_worktree_for_branch(branch: str) -> Path | None:
    entries = _worktrees()
    ref = f"refs/heads/{branch}"
    for entry in entries:
        if entry.get("branch") == ref:
            return Path(entry["worktree"])
    return None
