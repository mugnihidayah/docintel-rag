import socket

import pytest


def _port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.fixture
def require_db() -> None:
    if not _port_open("localhost", 5432):
        pytest.skip("Postgres not running (start it: docker compose up -d db)")


@pytest.fixture(autouse=True)
def _disable_tracing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests deterministic regardless of any Langfuse keys in the environment."""
    import app.rag.query as query

    monkeypatch.setattr(query, "get_tracer", lambda: None)
