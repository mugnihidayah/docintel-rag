from types import SimpleNamespace

import pytest

import app.ingestion.vision as vision_mod


def _settings(**kw: object) -> SimpleNamespace:
    base = {
        "vision_enabled": True,
        "vision_key": "k",
        "vision_min_image_kb": 20,
        "vision_base_url": "http://x",
        "vision_model": "m",
        "vision_timeout_s": 30.0,
    }
    base.update(kw)
    return SimpleNamespace(**base)


def test_describe_image_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vision_mod, "get_settings", lambda: _settings(vision_enabled=False))
    assert vision_mod.describe_image(b"x" * 100_000, "image/png") is None


def test_describe_image_small_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vision_mod, "get_settings", lambda: _settings())
    assert vision_mod.describe_image(b"tiny", "image/png") is None


def test_describe_image_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vision_mod, "get_settings", lambda: _settings())
    monkeypatch.setattr(vision_mod, "_call_vision", lambda *a, **k: "a diagram of X")
    assert vision_mod.describe_image(b"x" * 50_000, "image/png") == "a diagram of X"


def test_describe_image_failure_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*a: object, **k: object) -> str:
        raise RuntimeError("api down")

    monkeypatch.setattr(vision_mod, "get_settings", lambda: _settings())
    monkeypatch.setattr(vision_mod, "_call_vision", boom)
    assert vision_mod.describe_image(b"x" * 50_000, "image/png") is None
