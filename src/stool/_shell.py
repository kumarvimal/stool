"""
Shell utilities
~~~~~~~~~~~~~~~

Helper functions for shell operations and path management.
"""

from pathlib import Path
from typing import Iterator, Optional

# Project root directory (set by tasks.init())
root: Optional[Path] = None


def files(directory: Path, pattern: str) -> Iterator[Path]:
    """
    Find files matching a pattern in a directory.

    :param directory: Directory to search
    :param pattern: Glob pattern
    :return: Iterator of matching file paths
    """
    if not directory.exists():
        return

    for item in directory.rglob(pattern):
        if item.is_file():
            yield item


def find_user() -> str:
    """
    Find the current username.

    :return: Username
    """
    import getpass

    return getpass.getuser()
