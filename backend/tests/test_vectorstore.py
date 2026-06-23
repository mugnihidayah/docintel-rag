from types import SimpleNamespace

import pytest
from llama_index.vector_stores.postgres import PGVectorStore

from app.vectorstore import store as store_mod


def _settings(**kw: object) -> SimpleNamespace:
    base = {
        "database_url": "postgresql+asyncpg://docintel:docintel@localhost:5432/docintel",
        "embedding_dim": 1024,
    }
    base.update(kw)
    return SimpleNamespace(**base)


def test_make_vector_store_params(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_from_params(**kwargs: object) -> str:
        captured.update(kwargs)
        return "DUMMY_STORE"

    monkeypatch.setattr(PGVectorStore, "from_params", fake_from_params)

    result = store_mod.make_vector_store(_settings())

    assert result == "DUMMY_STORE"
    assert captured["hybrid_search"] is True
    assert captured["text_search_config"] == "simple"
    assert captured["embed_dim"] == 1024
    assert captured["host"] == "localhost"
    assert captured["database"] == "docintel"
    assert captured["hnsw_kwargs"]["hnsw_dist_method"] == "vector_cosine_ops"  # type: ignore[index]
