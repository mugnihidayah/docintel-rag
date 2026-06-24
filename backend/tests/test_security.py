import asyncio
from types import SimpleNamespace

import pytest

import app.api.security as security
from app.core.errors import RateLimitedError, UnauthorizedError


class _Req:
    def __init__(self, headers=None, host="1.2.3.4"):
        self.headers = headers or {}
        self.client = SimpleNamespace(host=host)


def test_api_key_noop_when_unset(monkeypatch) -> None:
    monkeypatch.setattr(security, "get_settings", lambda: SimpleNamespace(api_key=None))
    asyncio.run(security.require_api_key(_Req()))  # must not raise


def test_api_key_blocks_without_header(monkeypatch) -> None:
    monkeypatch.setattr(security, "get_settings", lambda: SimpleNamespace(api_key="secret"))
    with pytest.raises(UnauthorizedError):
        asyncio.run(security.require_api_key(_Req(headers={})))


def test_api_key_allows_with_header(monkeypatch) -> None:
    monkeypatch.setattr(security, "get_settings", lambda: SimpleNamespace(api_key="secret"))
    asyncio.run(security.require_api_key(_Req(headers={"X-API-Key": "secret"})))


def test_rate_limit_blocks_after_limit(monkeypatch) -> None:
    monkeypatch.setattr(security, "get_settings", lambda: SimpleNamespace(rate_limit_per_min=2))
    security._hits.clear()
    req = _Req(host="9.9.9.9")
    asyncio.run(security.rate_limit(req))
    asyncio.run(security.rate_limit(req))
    with pytest.raises(RateLimitedError):
        asyncio.run(security.rate_limit(req))


def test_rate_limit_disabled(monkeypatch) -> None:
    monkeypatch.setattr(security, "get_settings", lambda: SimpleNamespace(rate_limit_per_min=0))
    for _ in range(50):
        asyncio.run(security.rate_limit(_Req()))  # never raises
