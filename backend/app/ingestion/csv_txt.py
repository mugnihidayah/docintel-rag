"""CSV/TXT extractor: row/line blocks with line-range location"""

import csv
import hashlib
import io

from app.core.errors import ExtractionError
from app.ingestion.detector import register_extractor
from app.ingestion.models import Element, ElementType, ExtractedDocument, Location

_LINES_PER_BLOCK = 50


def _decode(data: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _build(
    filename: str,
    data: bytes,
    fmt: str,
    mime: str,
    elements: list[Element],
) -> ExtractedDocument:
    if not elements:
        raise ExtractionError(f"{fmt.upper()} has no extractable content")
    return ExtractedDocument(
        filename=filename,
        mime_type=mime,
        format=fmt,
        file_hash=hashlib.sha256(data).hexdigest(),
        size_bytes=len(data),
        elements=elements,
        num_units=None,
    )


def extract_csv(filename: str, data: bytes) -> ExtractedDocument:
    rows = list(csv.reader(io.StringIO(_decode(data))))
    while rows and not any(cell.strip() for cell in rows[-1]):
        rows.pop()

    elements: list[Element] = []
    if rows:
        header = " | ".join(rows[0])
        data_rows = rows[1:]
        for i in range(0, len(data_rows), _LINES_PER_BLOCK):
            block = data_rows[i : i + _LINES_PER_BLOCK]
            body = "\n".join(" | ".join(r) for r in block)
            elements.append(
                Element(
                    text=f"{header}\n{body}",
                    element_type=ElementType.CELL_BLOCK,
                    location=Location(row_start=i + 2, row_end=i + 1 + len(block)),
                )
            )
    return _build(filename, data, "csv", "text/csv", elements)


def extract_txt(filename: str, data: bytes) -> ExtractedDocument:
    lines = _decode(data).splitlines()
    elements: list[Element] = []
    for i in range(0, len(lines), _LINES_PER_BLOCK):
        block = lines[i : i + _LINES_PER_BLOCK]
        text = "\n".join(block).strip()
        if text:
            elements.append(
                Element(
                    text=text,
                    element_type=ElementType.PARAGRAPH,
                    location=Location(row_start=i + 1, row_end=i + len(block)),
                )
            )
    return _build(filename, data, "txt", "text/plain", elements)


register_extractor("csv", extract_csv)
register_extractor("txt", extract_txt)
