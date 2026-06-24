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
    assert d.metadata["source_id"] == "doc-123"  # queryable mirror (not overwritten by store)
    assert d.metadata["filename"] == "sop.pdf"
    assert d.metadata["page"] == 4
    assert d.metadata["element_type"] == "paragraph"
    # metadata kept out of the embedded text
    assert "page" in d.excluded_embed_metadata_keys


def test_to_documents_groups_section_with_its_items() -> None:
    extracted = ExtractedDocument(
        filename="brief.docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        format="docx",
        file_hash="x",
        size_bytes=1,
        elements=[
            Element("6. Penilaian", ElementType.PARAGRAPH, Location(block_index=35)),
            Element("- Parsing 25%", ElementType.PARAGRAPH, Location(block_index=36)),
            Element("- Arsitektur 25%", ElementType.PARAGRAPH, Location(block_index=37)),
            Element("7. Pengumpulan", ElementType.PARAGRAPH, Location(block_index=42)),
        ],
        num_units=4,
    )
    docs = to_documents(extracted, document_id="d1")

    assert len(docs) == 2  # [Penilaian + its items], [Pengumpulan]
    assert "Penilaian" in docs[0].text
    assert "Parsing 25%" in docs[0].text and "Arsitektur 25%" in docs[0].text
    assert docs[0].metadata["block_index"] == 35  # anchored to the heading


def test_all_extractors_registered() -> None:
    import app.ingestion  # noqa: F401  -> triggers registration of all formats
    from app.ingestion.detector import get_extractor

    for fmt in ("pdf", "docx", "pptx", "xlsx", "csv", "txt"):
        assert get_extractor(fmt)
