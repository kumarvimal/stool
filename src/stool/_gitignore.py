"""Manage Stool's entry in Git's global ignore file."""

import os
import subprocess
from pathlib import Path


def ensure_worktree_ignored() -> None:
    """Preserve global ignore rules and append the worktree directory rule."""
    result = subprocess.run(
        ["git", "config", "--global", "--path", "--get", "core.excludesFile"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise subprocess.CalledProcessError(
            result.returncode, result.args, output=result.stdout, stderr=result.stderr
        )
    if result.returncode == 0:
        path = Path(result.stdout.strip()).expanduser()
    else:
        config_home = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        path = config_home / "git" / "ignore"
    content = path.read_text() if path.exists() else ""
    if ".worktree/" in content.splitlines():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        if content and not content.endswith("\n"):
            stream.write("\n")
        stream.write(".worktree/\n")
