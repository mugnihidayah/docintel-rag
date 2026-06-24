import pytest
from fastapi.testclient import TestClient

import app.api.routes.documents as docs
from app.api.security import require_api_key
from app.main import app
from app.storage.storage import _safe_name


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[require_api_key] = lambda: None
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_safe_name_strips_path() -> None:
    assert _safe_name("../../etc/passwd") == "passwd"
    assert "/" not in _safe_name("a/b/c.pdf")
    assert _safe_name("weird name!@#.txt").endswith(".txt")


def test_upload_and_dedup(require_db: None, client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(docs, "index_document", lambda *a, **k: 3)
    monkeypatch.setattr(docs, "save_file", lambda *a, **k: "/tmp/fake")

    files = {"file": ("notes.txt", b"audit hello world via route test", "text/plain")}
    r1 = client.post("/documents", files=files)
    assert r1.status_code == 201
    b1 = r1.json()
    assert b1["status"] == "indexed"
    assert b1["num_chunks"] == 3

    r2 = client.post("/documents", files=files)
    assert r2.status_code == 201
    assert r2.json()["id"] == b1["id"]  # dedup: same bytes -> same record


def test_list_get_delete(require_db: None, client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(docs, "index_document", lambda *a, **k: 2)
    monkeypatch.setattr(docs, "save_file", lambda *a, **k: "/tmp/fake")

    files = {"file": ("crud.txt", b"crud lifecycle unique content 4242", "text/plain")}
    doc_id = client.post("/documents", files=files).json()["id"]

    listed = client.get("/documents")
    assert listed.status_code == 200
    assert any(d["id"] == doc_id for d in listed.json())

    got = client.get(f"/documents/{doc_id}")
    assert got.status_code == 200
    assert got.json()["filename"] == "crud.txt"

    assert client.get("/documents/nonexistent").status_code == 404

    assert client.delete(f"/documents/{doc_id}").status_code == 204
    assert client.get(f"/documents/{doc_id}").status_code == 404


def test_document_chunks(require_db: None, client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(docs, "index_document", lambda *a, **k: 1)
    monkeypatch.setattr(docs, "save_file", lambda *a, **k: "/tmp/fake")

    files = {"file": ("chunks.txt", b"chunk endpoint unique content 7777", "text/plain")}
    doc_id = client.post("/documents", files=files).json()["id"]

    res = client.get(f"/documents/{doc_id}/chunks")
    assert res.status_code == 200
    body = res.json()
    assert body["document_id"] == doc_id
    assert body["filename"] == "chunks.txt"
    assert isinstance(body["chunks"], list)  # empty here: indexing was mocked (no real nodes)

    assert client.get("/documents/nonexistent/chunks").status_code == 404
    assert client.get("/documents/nonexistent/file").status_code == 404
    client.delete(f"/documents/{doc_id}")  # cleanup
