from fastapi.testclient import TestClient

import app.api.routes.query as query_route
from app.main import app
from app.rag.query import Citation, QueryResult


def test_query_returns_answer_and_citations(monkeypatch) -> None:
    fake = QueryResult(
        answer="Audit dilakukan bulanan.",
        citations=[
            Citation(
                document_id="d1",
                filename="sop.pdf",
                location={"page": 2},
                snippet="Audit lini X bulanan.",
                score=0.91,
                score_type="rerank",
            )
        ],
        retrieved_chunks=1,
        model="groq:m",
        latency_ms=12,
    )
    monkeypatch.setattr(query_route, "answer_query", lambda *a, **k: fake)

    with TestClient(app) as client:
        resp = client.post("/query", json={"question": "Kapan audit lini X?"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "Audit dilakukan bulanan."
    assert body["retrieved_chunks"] == 1
    cit = body["citations"][0]
    assert cit["filename"] == "sop.pdf"
    assert cit["location"] == {"page": 2}
    assert cit["score_type"] == "rerank"


def test_query_rejects_empty_question() -> None:
    with TestClient(app) as client:
        resp = client.post("/query", json={"question": ""})
    assert resp.status_code == 422
