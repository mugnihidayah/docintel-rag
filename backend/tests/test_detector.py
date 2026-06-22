import io
import zipfile

import pytest

from app.core.errors import UnsupportedFormatError
from app.ingestion.detector import detect_format

PDF_BYTES = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n"
CSV_BYTES = b"name,age\nAlice,30\nBob,25\n"


def _make_zip() -> bytes:
    """A real, structurally valid zip so libmagic reports application/zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
    return buf.getvalue()


ZIP_BYTES = _make_zip()


def test_detect_pdf() -> None:
    assert detect_format("doc.pdf", PDF_BYTES) == "pdf"


def test_detect_csv() -> None:
    assert detect_format("data.csv", CSV_BYTES) == "csv"


def test_detect_docx_by_extension() -> None:
    assert detect_format("report.docx", ZIP_BYTES) == "docx"


def test_unsupported_extension() -> None:
    with pytest.raises(UnsupportedFormatError):
        detect_format("archive.rar", b"whatever")


def test_extension_content_mismatch() -> None:
    with pytest.raises(UnsupportedFormatError):
        detect_format("fake.txt", PDF_BYTES)  # PDF content disguised as .txt
