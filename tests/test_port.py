from unittest.mock import Mock

import invoke
import pytest

from stool.port import clear_used_port
from stool.settings import create_env


@pytest.mark.parametrize(
    ("settings", "port", "expected"),
    [
        ({}, None, 8000),
        ({"default_port": 9000}, None, 9000),
        ({"default_port": 9000}, 7000, 7000),
    ],
)
def test_clear_port_selection(monkeypatch, settings, port, expected):
    run = Mock()
    monkeypatch.setattr(invoke.Context, "run", run)
    ctx = invoke.Context(config=invoke.Config(overrides=settings))
    clear_used_port(ctx, port)
    command = run.call_args.args[0]
    assert f"lsof -ti tcp:{expected} -sTCP:LISTEN" in command
    assert f"No process listening on port {expected}" in command


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_invalid_port_does_not_run_command(monkeypatch, port):
    run = Mock()
    monkeypatch.setattr(invoke.Context, "run", run)
    with pytest.raises(ValueError, match="port must be between"):
        clear_used_port(invoke.Context(), port)
    run.assert_not_called()


def test_project_can_override_default_port():
    assert create_env().default_port == 8000
    assert create_env(default_port=9000).default_port == 9000
