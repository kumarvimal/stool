"""Worktree creation and project-local file setup."""

import re
import shutil
import subprocess
from pathlib import Path

from ._git import (
    _branch_exists,
    _linked_worktree_for_branch,
    _repo_root,
    _validate_branch,
)
from ._gitignore import ensure_worktree_ignored


def setup_paths(
    root: Path, destination: Path, symlinks: list[str], copies: list[str]
) -> list[str]:
    """Populate missing paths without replacing existing worktree files."""
    prepared = []
    for names, copy in ((symlinks, False), (copies, True)):
        for name in names:
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"Worktree paths must be project-relative: {name}")
            source = root / relative
            target = destination / relative
            if not source.exists() or target.exists() or target.is_symlink():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if not copy:
                target.symlink_to(source, target_is_directory=source.is_dir())
            elif source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
            prepared.append(name)
    return prepared


def create_worktree(
    branch: str,
    path: str | None = None,
    *,
    symlinks: list[str],
    copies: list[str],
) -> str:
    """Create or reuse a branch checkout, then apply project settings."""
    _validate_branch(branch)
    root = _repo_root()
    suffix = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip(".-")
    destination = (
        Path(path).expanduser() if path else root / ".worktree" / suffix
    ).resolve()
    ensure_worktree_ignored()
    existing = _linked_worktree_for_branch(branch)
    if existing is not None:
        destination = existing
        message = f"{branch} already has a worktree at {destination}"
    else:
        exists = _branch_exists(branch)
        command = ["git", "worktree", "add"]
        if not exists:
            command.extend(["-b", branch])
        command.append(str(destination))
        if exists:
            command.append(branch)
        subprocess.run(command, check=True)
        message = f"created {destination}"
    prepared = setup_paths(root, destination, symlinks, copies)
    return f"{message}\nprepared local paths: {', '.join(prepared) or 'none'}\n"
