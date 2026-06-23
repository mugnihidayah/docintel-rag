from app.ingestion.models import Element, ElementType, ExtractedDocument, Location
from app.ingestion.normalizer import to_documents


def test_to_documents_carries_metadata() -> None:
    extracted = ExtractedDocument(
        filename="sop.pdf",
        mime_type="application/pdf",
        format="pdf",
        file_hash="abc",
        size_bytes=10,
        elements=[
            Element(
                text="Audit procedure for line X",
                element_type=ElementType.PARAGRAPH,
                location=Location(page=4),
            )
        ],
        num_units=12,
    )
    docs = to_documents(extracted, document_id="doc-123")

    assert len(docs) == 1
    d = docs[0]
    assert d.text == "Audit procedure for line X"
    assert d.metadata["document_id"] == "doc-123"
    assert d.metadata["filename"] == "sop.pdf"
    assert d.metadata["page"] == 4
    assert d.metadata["element_type"] == "paragraph"
    # metadata kept out of the embedded text
    assert "page" in d.excluded_embed_metadata_keys


def test_all_extractors_registered() -> None:
    import app.ingestion  # noqa: F401  -> triggers registration of all formats
    from app.ingestion.detector import get_extractor

    for fmt in ("pdf", "docx", "pptx", "xlsx", "csv", "txt"):
        assert get_extractor(fmt)
