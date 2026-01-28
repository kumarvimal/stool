"""
Task definitions for this project.

This file bootstraps stool and makes all commands available.
Run 'inv -l' to see available tasks.
"""

from stool.tasks import init as namespace

namespace = namespace(__file__)
