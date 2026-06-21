from app.core.config import get_settings
from app.core.errors import NotFoundError


def test_settings_defaults() -> None:
    settings = get_settings()
    assert settings.embedding_dim == 1024
    assert settings.retrieve_top_k == 30


def test_app_error_maps_to_http() -> None:
    err = NotFoundError("missing")
    assert (err.status_code, err.code, err.detail) == (404, "not_found", "missing")
