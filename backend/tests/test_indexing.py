import pytest
from llama_index.core.embeddings import MockEmbedding

import app.rag.indexer as indexer


def test_index_document_into_pgvector(require_db: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        indexer, "make_embed_model", lambda settings=None: MockEmbedding(embed_dim=1024)
    )
    data = b"line one about audit procedures\nline two about safety checks\n" * 5
    count = indexer.index_document("notes.txt", data, "doc-integration-1")
    assert count >= 1
