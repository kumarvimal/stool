"""
Command-line interface
~~~~~~~~~~~~~~~~~~~~~~

Minimal standalone CLI that creates tasks.py.
Once tasks.py exists, users can access full stool commands.
"""

import sys
from importlib.metadata import version
from pathlib import Path

from invoke import Program


def run() -> None:
    """Run Invoke using Stool's installed environment."""
    Program(name="Stool", binary="stool", version=version("stool")).run()


TASKS_PY_CONTENT = '''"""
Task definitions for this project.

This file bootstraps stool and makes all commands available.
Run 'stool -l' to see available tasks.
"""

from stool.tasks import init as namespace

namespace = namespace(__file__)
'''


def init_project():
    """
    Initialize stool by creating tasks.py.

    This minimal bootstrap creates only tasks.py.
    After that, use 'stool init.project' for full setup.

    Can be run without existing tasks.py file.
    """
    project_root = Path.cwd()

    print("🔧 Bootstrapping stool...")
    print(f"📁 Project root: {project_root}")
    print()

    # Create tasks.py
    tasks_file = project_root / "tasks.py"
    if tasks_file.exists():
        print(f"⚠️  tasks.py already exists!")
        print()
        print("Next steps:")
        print("  Run 'stool init.project' to complete setup")
        return

    tasks_file.write_text(TASKS_PY_CONTENT)
    print(f"✓ Created {tasks_file}")
    print()
    print("✓ Bootstrap complete!")
    print()
    print("Next steps:")
    print("  1. Run 'stool init.project' to create _stool/ directory and settings")
    print("  2. Or run 'stool -l' to see all available commands")


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("stool-init - Initialize stool in the current project")
        print()
        print("Usage:")
        print("  stool-init")
        print()
        print("This creates:")
        print("  - tasks.py (2 lines)")
        print("  - _stool/ directory for custom tasks")
        print("  - _stool/_settings.py for configuration")
        print()
        print("After initialization, use 'stool -l' to see available tasks.")
        sys.exit(0)

    try:
        init_project()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
