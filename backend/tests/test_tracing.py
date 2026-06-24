from types import SimpleNamespace

import app.observability.tracing as tracing


def test_tracer_disabled_when_no_keys(monkeypatch) -> None:
    tracing.get_tracer.cache_clear()
    monkeypatch.setattr(tracing, "get_settings", lambda: SimpleNamespace(langfuse_enabled=False))

    assert tracing.get_tracer() is None
    tracing.flush()  # no-op when disabled, must not raise

    tracing.get_tracer.cache_clear()
