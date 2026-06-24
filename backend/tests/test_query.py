from types import SimpleNamespace

from llama_index.core.schema import NodeWithScore, TextNode

import app.rag.query as q
from app.rag.query import _build_citations


class _Resp:
    def __init__(self, text: str) -> None:
        self.text = text

    def __str__(self) -> str:
        return self.text


def _node(text: str, **meta: object) -> NodeWithScore:
    return NodeWithScore(node=TextNode(text=text, metadata=meta), score=0.83)


def _fake_settings() -> SimpleNamespace:
    return SimpleNamespace(rerank_top_n=5, llm_provider="groq", llm_model="m")


def test_build_citations() -> None:
    node = _node("Audit procedure X.", document_id="d1", filename="sop.pdf", page=4)
    cits = _build_citations([node], "rerank")

    assert len(cits) == 1
    c = cits[0]
    assert (c.document_id, c.filename, c.score_type) == ("d1", "sop.pdf", "rerank")
    assert c.location == {"page": 4}
    assert "Audit procedure" in c.snippet


def test_answer_query_grounded(monkeypatch) -> None:
    nodes = [_node("Audit lini X bulanan.", document_id="d1", filename="sop.pdf", page=2)]
    retriever = SimpleNamespace(retrieve=lambda _q: nodes)
    llm = SimpleNamespace(complete=lambda _p: _Resp("Audit bulanan."))

    monkeypatch.setattr(q, "make_retriever", lambda s=None: retriever)
    monkeypatch.setattr(q, "make_reranker", lambda s=None: None)
    monkeypatch.setattr(q, "make_llm", lambda s=None: llm)
    monkeypatch.setattr(q, "get_settings", _fake_settings)

    result = q.answer_query("Kapan audit lini X?")

    assert result.answer == "Audit bulanan."
    assert result.retrieved_chunks == 1
    assert result.citations[0].score_type == "hybrid"
    assert result.model == "groq:m"


def test_answer_query_not_found_drops_citations(monkeypatch) -> None:
    # retrieval returns weakly-related chunks, but the grounded answer is "not found"
    nodes = [_node("Topik tak relevan.", document_id="d9", filename="lain.pdf", page=1)]
    retriever = SimpleNamespace(retrieve=lambda _q: nodes)
    llm = SimpleNamespace(complete=lambda _p: _Resp("Tidak ditemukan dalam dokumen."))

    monkeypatch.setattr(q, "make_retriever", lambda s=None: retriever)
    monkeypatch.setattr(q, "make_reranker", lambda s=None: None)
    monkeypatch.setattr(q, "make_llm", lambda s=None: llm)
    monkeypatch.setattr(q, "get_settings", _fake_settings)

    result = q.answer_query("Apakah ada SOP penggunaan AI generatif?")

    assert result.answer == "Tidak ditemukan dalam dokumen."
    assert result.citations == []  # no citations on a not-found answer
    assert result.retrieved_chunks == 1  # retrieval still happened (transparency)


def test_answer_query_rerank_fallback(monkeypatch) -> None:
    nodes = [_node("Audit lini X bulanan.", document_id="d1", filename="sop.pdf", page=2)]

    class _BadReranker:
        def postprocess_nodes(self, nodes, query_str=None):  # type: ignore[no-untyped-def]
            raise RuntimeError("cohere down")

    retriever = SimpleNamespace(retrieve=lambda _q: nodes)
    llm = SimpleNamespace(complete=lambda _p: _Resp("Jawab."))

    monkeypatch.setattr(q, "make_retriever", lambda s=None: retriever)
    monkeypatch.setattr(q, "make_reranker", lambda s=None: _BadReranker())
    monkeypatch.setattr(q, "make_llm", lambda s=None: llm)
    monkeypatch.setattr(q, "get_settings", _fake_settings)

    result = q.answer_query("Kapan?")

    assert result.answer == "Jawab."
    # rerank gagal -> fallback ke urutan retriever
    assert result.citations[0].score_type == "hybrid"
