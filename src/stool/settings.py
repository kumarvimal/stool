"""
Settings management
~~~~~~~~~~~~~~~~~~~

Configuration and settings for stool.
"""

from pathlib import Path
from typing import Any, Dict, List, Set

from . import _shell


class Settings(dict):
    """Settings dictionary with attribute access."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__ = self


def create_env(**kwargs: Any) -> Settings:
    """
    Create base environment settings.

    :param kwargs: Additional settings to merge
    :return: Settings object
    """
    result = Settings(
        user=_shell.find_user(),
        disabled_tasks=[],
        **kwargs
    )
    return result


def load() -> Settings:
    """
    Load final settings from third-party project.

    This attempts to import settings from the local '_stool' module
    in the third-party project.

    :return: Settings object
    """
    try:
        from _stool import _settings
        return _settings.env
    except (ImportError, AttributeError):
        return create_env()
