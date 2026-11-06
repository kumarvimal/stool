import subprocess

import pytest

from stool._gitignore import ensure_worktree_ignored
from stool._worktree import create_worktree, setup_paths


@pytest.fixture
def repository(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.chdir(root)
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--allow-empty",
            "-qm",
            "initial",
        ],
        check=True,
    )
    return root


def test_create_reuse_and_prepare(repository):
    root = repository
    (root / ".env").write_text("local")
    (root / "assets").mkdir()
    (root / "assets/build").write_text("compiled")
    result = create_worktree("feat/example", symlinks=["assets"], copies=[".env"])
    destination = root / ".worktree/feat-example"
    assert str(destination) in result
    assert (destination / "assets").is_symlink()
    assert (destination / ".env").read_text() == "local"
    assert not (destination / ".env").is_symlink()
    (destination / ".env").write_text("changed")
    (destination / "assets").unlink()
    assert "already has a worktree" in create_worktree(
        "feat/example", symlinks=["assets"], copies=[".env"]
    )
    assert (destination / "assets").is_symlink()
    assert (destination / ".env").read_text() == "changed"
    assert (
        subprocess.run(
            ["git", "check-ignore", str(destination)], capture_output=True
        ).returncode
        == 0
    )


def test_existing_branch_explicit_path_empty_settings(repository):
    subprocess.run(["git", "branch", "existing"], check=True)
    destination = repository.parent / "custom"
    create_worktree("existing", str(destination), symlinks=[], copies=[])
    assert (destination / ".git").is_file()
    assert not (destination / ".env").exists()


def test_configured_global_ignore_preserved(repository):
    ignore = repository.parent / "custom-ignore"
    ignore.write_text("other-pattern")
    subprocess.run(
        ["git", "config", "--global", "core.excludesFile", str(ignore)], check=True
    )
    ensure_worktree_ignored()
    ensure_worktree_ignored()
    assert ignore.read_text() == "other-pattern\n.worktree/\n"


def test_ignore_failure_stops_creation(repository):
    ignore = repository.parent / "ignore-directory"
    ignore.mkdir()
    subprocess.run(
        ["git", "config", "--global", "core.excludesFile", str(ignore)], check=True
    )
    with pytest.raises(IsADirectoryError):
        create_worktree("blocked", symlinks=[], copies=[])
    assert not (repository / ".worktree/blocked").exists()


def test_setup_copies_directories_and_preserves_dangling_links(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "folder").mkdir()
    (root / "folder/file").write_text("content")
    destination = tmp_path / "destination"
    destination.mkdir()
    setup_paths(root, destination, [], ["folder", "missing"])
    assert (destination / "folder/file").read_text() == "content"
    assert not (destination / "folder").is_symlink()
    (destination / "link").symlink_to(tmp_path / "missing")
    (root / "link").write_text("source")
    assert setup_paths(root, destination, ["link"], []) == []


@pytest.mark.parametrize("name", ["/absolute", "../outside"])
def test_reject_non_relative_paths(tmp_path, name):
    with pytest.raises(ValueError):
        setup_paths(tmp_path, tmp_path, [name], [])
