from types import SimpleNamespace

from llama_index.core import Document

from app.chunking.chunker import chunk_documents


def _settings(**kw: object) -> SimpleNamespace:
    base = {"chunk_size": 512, "chunk_overlap": 64}
    base.update(kw)
    return SimpleNamespace(**base)


def test_chunk_preserves_metadata() -> None:
    long_text = " ".join(f"This is sentence number {i}." for i in range(300))
    doc = Document(text=long_text, metadata={"document_id": "d1", "page": 3, "filename": "a.pdf"})
    nodes = chunk_documents([doc], _settings())

    assert len(nodes) >= 1
    assert all(n.metadata["page"] == 3 for n in nodes)
    assert all(n.metadata["document_id"] == "d1" for n in nodes)


def test_chunk_does_not_merge_documents() -> None:
    d1 = Document(text="Slide one content about apples.", metadata={"slide": 1})
    d2 = Document(text="Slide two content about bananas.", metadata={"slide": 2})
    nodes = chunk_documents([d1, d2], _settings())

    assert {n.metadata.get("slide") for n in nodes} == {1, 2}
    for n in nodes:
        assert not ("apples" in n.text and "bananas" in n.text)  # no cross-slide node
