import uuid
from types import SimpleNamespace

from llama_index.core.embeddings import MockEmbedding

import app.rag.indexer as indexer
import app.rag.query as query
import app.retrieval.retriever as retriever


class _Resp:
    def __init__(self, text: str) -> None:
        self.text = text

    def __str__(self) -> str:
        return self.text


def _mock_embed(settings: object = None) -> MockEmbedding:
    return MockEmbedding(embed_dim=1024)


def test_ingest_then_answer_end_to_end(require_db: None, monkeypatch) -> None:
    # Mock embeddings on both write (index) and read (retrieve) paths -> no embedding API.
    monkeypatch.setattr(indexer, "make_embed_model", _mock_embed)
    monkeypatch.setattr(retriever, "make_embed_model", _mock_embed)
    # No reranker (skip Cohere) and a stub LLM (skip Groq) -> deterministic & offline.
    answer = "Prosedur audit dilakukan harian."
    llm = SimpleNamespace(complete=lambda _p: _Resp(answer))
    monkeypatch.setattr(query, "make_reranker", lambda s=None: None)
    monkeypatch.setattr(query, "make_llm", lambda s=None: llm)

    marker = f"zylophonics{uuid.uuid4().hex[:8]}"
    filename = f"e2e-{marker}.txt"
    body = f"Prosedur audit {marker} dilakukan harian oleh tim mutu.\n"
    data = (body * 3).encode()

    count = indexer.index_document(filename, data, f"doc-{marker}")
    assert count >= 1

    result = query.answer_query(f"Kapan prosedur audit {marker} dilakukan?")

    assert result.answer == answer
    mine = [c for c in result.citations if c.filename == filename]
    assert mine, "expected a citation from the freshly ingested document"
    assert mine[0].location  # has a source location (line range)
