"""utilities"""


def confirm(prompt="Are you sure?", default=False):
    """Confirm a prompt with optional default."""
    suffix = "[Y/n]" if default else "[y/N]"
    resp = input(f"{prompt} {suffix}: ").strip().lower()

    if not resp:
        return default
    return resp in ("y", "yes")
