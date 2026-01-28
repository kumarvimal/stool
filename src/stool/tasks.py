"""
Task discovery and management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Core logic for discovering and merging builtin and local tasks.
"""

import importlib
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterator, List, Set, Tuple

import invoke

from . import settings as _settings
from . import _shell


# Task collections by type
_SPACES: Dict[str, invoke.Collection] = {
    "default": invoke.Collection(),
    "BUILTIN": invoke.Collection(),
    "LOCAL": invoke.Collection(),
}


def init(tasks_file: str) -> invoke.Collection:
    """
    Create namespace merged from builtin + local tasks.

    This is the main entry point called from a third-party project's tasks.py.

    :param tasks_file: Path to the tasks.py file (use __file__)
    :return: Merged invoke Collection with all tasks
    """
    # Set project root
    _shell.root = Path(tasks_file).parent.resolve()

    # Add project root to sys.path for imports
    root_str = str(_shell.root)
    if root_str in sys.path:
        sys.path.remove(root_str)
    sys.path.insert(0, root_str)

    # Load settings
    env = _settings.load()

    # Parse disabled tasks
    disabled_spaces: Set[str] = set()
    disabled_tasks: Set[str] = set()
    for item in env.disabled_tasks:
        if item.endswith(".*"):
            disabled_spaces.add(item[:-2])
        else:
            disabled_tasks.add(item)
            disabled_spaces.add(item)

    # Collect tasks from all sources
    repair = []
    defaults = defaultdict(list)
    prefixed = defaultdict(lambda: defaultdict(dict))

    for provider in (builtin_modules, local_modules):
        pkg, prefix, modules = provider()
        assert prefix in _SPACES and prefix != "default"

        for module in modules:
            name = getattr(module, "NAMESPACE", None)
            if not name:
                # Derive namespace from module name
                name = module.__name__.split(".")[-1]
            assert "." not in name

            if prefix == "BUILTIN" and name in disabled_spaces:
                continue

            default = None
            for item in vars(module).values():
                if not isinstance(item, invoke.Task):
                    continue

                if prefix == "BUILTIN" and f"{name}.{item.name}" in disabled_spaces:
                    continue

                if item.is_default:
                    default = item

                repair.append(item)
                prefixed["default"][name][item.name] = item
                prefixed[prefix][name][item.name] = item

            if default is not None:
                defaults[name].append(default)

    # Fix overlapping defaults (keep latest)
    for tasks in defaults.values():
        if len(tasks) > 1:
            for task in tasks[:-1]:
                task.is_default = False

    # Build final collections
    final = {
        prefix: invoke.Collection(
            **{
                name: invoke.Collection(*tasks.values())
                for name, tasks in spaces.items()
            }
        )
        for prefix, spaces in prefixed.items()
    }

    for coll in final.values():
        coll.configure(env)

    _SPACES.update(final)

    # Transform string dependencies to real tasks
    for task in repair:
        for attr in ("pre", "post"):
            setattr(
                task,
                attr,
                [
                    (_SPACES["default"][item] if isinstance(item, str) else item)
                    for item in getattr(task, attr)
                ],
            )

    return _SPACES["default"]


def builtin_modules() -> Tuple[str, str, List[Any]]:
    """
    Find all builtin modules providing tasks.

    :return: Tuple of (package_name, prefix, modules)
    """
    path = Path(__file__).parent
    pkg = "stool"
    return pkg, "BUILTIN", list(_scan(path, pkg))


def local_modules() -> Tuple[str, str, List[Any]]:
    """
    Find all local modules providing tasks from third-party project.

    :return: Tuple of (package_name, prefix, modules)
    """
    if _shell.root is None:
        return "_stool", "LOCAL", []

    path = _shell.root / "_stool"
    pkg = "_stool"
    return pkg, "LOCAL", list(_scan(path, pkg))


def _scan(path: Path, pkg: str) -> Iterator[Any]:
    """
    Scan directory for modules containing invoke tasks.

    :param path: Directory to scan
    :param pkg: Package name
    :return: Iterator of modules containing tasks
    """
    if not path.exists():
        return

    is_valid = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\.py$").match

    for filepath in _shell.files(path, "*.py"):
        filename = filepath.name

        if not is_valid(filename):
            continue
        if filename == "__init__.py":
            continue
        if filename.startswith("_"):
            continue

        # Get module name
        modname = filename[:-3]
        qname = f"{pkg}.{modname}"

        try:
            module = importlib.import_module(qname)
        except ImportError:
            continue

        # Check if module has any tasks
        has_task = False
        for item in vars(module).values():
            if isinstance(item, invoke.Task):
                has_task = True
                break

        if has_task:
            yield module


def exists(name: str) -> bool:
    """
    Check if a task exists.

    :param name: Task name
    :return: True if task exists
    """
    return name in _SPACES["default"]


def context() -> invoke.Context:
    """
    Create an out-of-context invoke context.

    :return: Invoke context
    """
    config = invoke.Config()
    collection_config = _SPACES["default"].configuration()
    config.load_collection(collection_config)
    config.load_shell_env()
    return invoke.Context(config)
