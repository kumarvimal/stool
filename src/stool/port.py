"""Tasks for local development ports."""

import invoke


@invoke.task(aliases=["clear"])
def clear_used_port(ctx: invoke.Context, port: int | None = None) -> None:
    """Stop processes listening on PORT, or the project's default_port."""
    port = int(port if port is not None else ctx.config.get("default_port", 8000))
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    ctx.run(
        f"pids=$(lsof -ti tcp:{port} -sTCP:LISTEN); "
        f'if [ -n "$pids" ]; then kill $pids; '
        f'else echo "No process listening on port {port}"; fi',
        pty=True,
        echo=True,
    )
