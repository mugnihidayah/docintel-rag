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
