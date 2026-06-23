import pytest

from app.core.errors import ExtractionError, UnsupportedFormatError, ValidationError
from app.ingestion.pipeline import extract_to_documents


def test_corrupt_pdf_raises_extraction_error() -> None:
    with pytest.raises(ExtractionError):
        extract_to_documents("broken.pdf", b"%PDF-1.4\n garbage not a real pdf", "doc-1")


def test_unsupported_format_raises() -> None:
    with pytest.raises(UnsupportedFormatError):
        extract_to_documents("archive.rar", b"some bytes here", "doc-1")


def test_empty_file_raises() -> None:
    with pytest.raises(ValidationError):
        extract_to_documents("empty.txt", b"", "doc-1")


def test_pipeline_end_to_end_txt() -> None:
    docs = extract_to_documents("note.txt", b"line one\nline two\n", "doc-42")
    assert len(docs) == 1
    assert docs[0].metadata["document_id"] == "doc-42"
    assert docs[0].metadata["format"] == "txt"
    assert "line one" in docs[0].text
