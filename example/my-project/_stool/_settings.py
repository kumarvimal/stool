"""
Project settings for stool.

Configure stool behavior for this project.
"""

from stool.settings import create_env

env = create_env(
    # Project-specific settings
    project_name="my-project",
    # Optionally disable specific builtin tasks
    # disabled_tasks=[
    #     'hello.user',      # Disable specific task
    #     'init.*',          # Disable entire namespace
    # ],
    # Custom settings for your tasks
    deployment=dict(
        staging="staging.example.com",
        production="prod.example.com",
    ),
)
