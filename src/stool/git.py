"""Shared Git tasks."""

import sys

import invoke

from ._git import DEFAULT_BRANCH_COUNT, _latest_branches, _list_worktrees
from ._worktree import create_worktree


@invoke.task(aliases=["branches"])
def latest(ctx: invoke.Context, number: int = DEFAULT_BRANCH_COUNT) -> None:
    """List the most recently updated local branches."""
    sys.stdout.write(_latest_branches(int(number)))


@invoke.task(aliases=["wt"])
def worktree(ctx: invoke.Context, branch: str, path: str | None = None) -> None:
    """Create a Git worktree under .worktree/ and prepare project-local files."""
    sys.stdout.write(
        create_worktree(
            branch,
            path,
            symlinks=ctx.config.get("worktree_symlink", []),
            copies=ctx.config.get("worktree_copy", []),
        )
    )


@invoke.task(name="list", aliases=["worktrees"])
def list_worktrees(ctx: invoke.Context) -> None:
    """List Git worktrees."""
    sys.stdout.write(_list_worktrees())
