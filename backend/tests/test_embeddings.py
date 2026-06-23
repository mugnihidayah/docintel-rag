from types import SimpleNamespace

import pytest

from app.embeddings.factory import make_embed_model


def _settings(**kw: object) -> SimpleNamespace:
    base = {
        "embedding_provider": "jina",
        "embedding_api_key": "test-key",
        "embedding_model": "jina-embeddings-v3",
    }
    base.update(kw)
    return SimpleNamespace(**base)


def test_make_embed_model_jina() -> None:
    from llama_index.embeddings.jinaai import JinaEmbedding

    model = make_embed_model(_settings())
    assert isinstance(model, JinaEmbedding)


def test_make_embed_model_unknown_provider_raises() -> None:
    with pytest.raises(ValueError):
        make_embed_model(_settings(embedding_provider="unknown"))
