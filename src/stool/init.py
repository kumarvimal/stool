"""
Project initialization
~~~~~~~~~~~~~~~~~~~~~~

Commands to initialize stool in a third-party project.
"""

import subprocess
from pathlib import Path

import invoke

TASKS_PY_CONTENT = '''"""
Task definitions for this project.

This file bootstraps stool and makes all commands available.
Run 'inv -l' to see available tasks.
"""

from stool.tasks import init as namespace

namespace = namespace(__file__)
'''


TOOL_DIR_INIT = '''"""
Custom tasks for this project.

Add your project-specific tasks here.
"""
'''


SETTINGS_CONTENT = '''"""
Project settings for stool.

Configure stool behavior for this project.
"""

from stool.settings import create_env

env = create_env(
    # Add your project-specific settings here
    # disabled_tasks=['hello.*'],  # Disable specific tasks
)
'''


@invoke.task(default=True)
def project(ctx, add_to_gitignore=False, global_gitignore=False):
    """
    Initialize stool in the current project.

    Creates the necessary files to enable stool in a third-party project:
    - tasks.py: Bootstrap file (if missing)
    - _stool/: Directory for custom tasks
    - _stool/_settings.py: Project settings

    :param add_to_gitignore: Add tasks.py and _stool/ to .gitignore
    :param global_gitignore: Add to global Git ignore instead of local
    """
    from . import _shell

    if shell.root is None:
        print("Error: No project root set")
        return

    project_root = shell.root

    # Create tasks.py if it doesn't exist
    tasks_file = project_root / "tasks.py"
    if not tasks_file.exists():
        tasks_file.write_text(TASKS_PY_CONTENT)
        print(f"✓ Created {tasks_file}")
    else:
        print(f"✓ tasks.py already exists")

    # Create _stool directory
    stool_dir = project_root / "_stool"
    stool_dir.mkdir(exist_ok=True)
    print(f"✓ Created {stool_dir}/")

    # Create _stool/__init__.py
    stool_init = stool_dir / "__init__.py"
    if not stool_init.exists():
        stool_init.write_text(TOOL_DIR_INIT)
        print(f"✓ Created {stool_init}")

    # Create _stool/_settings.py
    settings_file = stool_dir / "_settings.py"
    if not settings_file.exists():
        settings_file.write_text(SETTINGS_CONTENT)
        print(f"✓ Created {settings_file}")

    # Handle gitignore
    if add_to_gitignore or global_gitignore:
        _add_to_gitignore(
            project_root,
            global_ignore=global_gitignore
        )

    print("\n✓ Initialization complete!")
    print("\nNext steps:")
    print("  1. Run 'inv -l' to see available tasks")
    print("  2. Add custom tasks in _stool/ directory")
    print("  3. Configure settings in _stool/_settings.py")


def _add_to_gitignore(project_root: Path, global_ignore: bool = False):
    """
    Add stool files to gitignore.

    :param project_root: Project root directory
    :param global_ignore: Use global gitignore instead of local
    """
    entries = [
        "# stool task management",
        "tasks.py",
        "_stool/",
    ]

    if global_ignore:
        # Add to global gitignore
        result = subprocess.run(
            ["git", "config", "--global", "core.excludesfile"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            global_ignore_path = Path(result.stdout.strip()).expanduser()
        else:
            # Default location
            global_ignore_path = Path.home() / ".gitignore_global"

            # Set it as the global excludesfile
            subprocess.run(
                [
                    "git",
                    "config",
                    "--global",
                    "core.excludesfile",
                    str(global_ignore_path),
                ],
                check=False,
            )

        _append_to_gitignore(global_ignore_path, entries)
        print(f"✓ Added to global gitignore: {global_ignore_path}")
    else:
        # Add to local .gitignore
        local_gitignore = project_root / ".gitignore"
        _append_to_gitignore(local_gitignore, entries)
        print(f"✓ Added to local gitignore: {local_gitignore}")


def _append_to_gitignore(gitignore_path: Path, entries: list):
    """
    Append entries to gitignore file if they don't exist.

    :param gitignore_path: Path to gitignore file
    :param entries: List of entries to add
    """
    if gitignore_path.exists():
        content = gitignore_path.read_text()
    else:
        content = ""

    # Check which entries are missing
    missing = []
    for entry in entries:
        if entry.startswith("#"):
            continue
        if entry not in content:
            missing.append(entry)

    if missing:
        # Add entries
        if content and not content.endswith("\n"):
            content += "\n"

        content += "\n" + "\n".join(entries) + "\n"
        gitignore_path.write_text(content)


@invoke.task()
def clean(ctx):
    """
    Remove stool files from the current project.

    Removes:
    - tasks.py
    - _stool/ directory

    Warning: This will delete custom tasks!
    """
    from . import _shell

    if shell.root is None:
        print("Error: No project root set")
        return

    project_root = shell.root

    print("⚠ This will remove stool files from the project:")
    print(f"  - {project_root / 'tasks.py'}")
    print(f"  - {project_root / '_stool'}/")
    print("\nThis action cannot be undone!")

    response = input("Continue? (y/N): ").strip().lower()
    if response != "y":
        print("Cancelled")
        return

    # Remove tasks.py
    tasks_file = project_root / "tasks.py"
    if tasks_file.exists():
        tasks_file.unlink()
        print(f"✓ Removed {tasks_file}")

    # Remove _stool directory
    stool_dir = project_root / "_stool"
    if stool_dir.exists():
        import shutil
        shutil.rmtree(stool_dir)
        print(f"✓ Removed {stool_dir}/")

    print("\n✓ Cleanup complete")
