"""
Hello world commands
~~~~~~~~~~~~~~~~~~~~

Example commands to demonstrate stool functionality.
"""

import invoke


@invoke.task(default=True)
def user(ctx):
    """
    Greet the current user.

    Displays a personalized greeting using the username
    from the environment settings.
    """
    username = ctx.get("user", "friend")
    print(f"Hello, {username}!")
