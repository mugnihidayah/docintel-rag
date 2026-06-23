from types import SimpleNamespace

import pytest

import app.retrieval.retriever as retr
from app.retrieval.retriever import make_reranker


def _settings(**kw: object) -> SimpleNamespace:
    base = {
        "rerank_enabled": True,
        "cohere_api_key": "test-key",
        "rerank_model": "rerank-multilingual-v3.0",
        "rerank_top_n": 5,
    }
    base.update(kw)
    return SimpleNamespace(**base)


def test_make_reranker_disabled_returns_none() -> None:
    assert make_reranker(_settings(rerank_enabled=False)) is None


def test_make_reranker_no_key_returns_none() -> None:
    assert make_reranker(_settings(cohere_api_key=None)) is None


def test_make_reranker_enabled_returns_cohere() -> None:
    from llama_index.postprocessor.cohere_rerank import CohereRerank

    assert isinstance(make_reranker(_settings()), CohereRerank)


def test_make_retriever_builds(require_db: None, monkeypatch: pytest.MonkeyPatch) -> None:
    from llama_index.core.embeddings import MockEmbedding

    monkeypatch.setattr(
        retr, "make_embed_model", lambda settings=None: MockEmbedding(embed_dim=1024)
    )
    retriever = retr.make_retriever()
    assert hasattr(retriever, "retrieve")
