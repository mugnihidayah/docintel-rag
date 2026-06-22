"""DOCX extractor: paragraphs, headings, tables + image understanding."""

import hashlib
import io
from collections.abc import Iterator

from docx import Document as open_docx
from docx.document import Document
from docx.oxml.ns import qn
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.core.errors import ExtractionError
from app.ingestion.detector import register_extractor
from app.ingestion.models import Element, ElementType, ExtractedDocument, Location
from app.ingestion.vision import images_to_elements

_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _iter_blocks(doc: Document) -> Iterator[Paragraph | Table]:
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield Table(child, doc)


def _para_type(style_name: str) -> ElementType:
    if style_name.startswith("Heading") or style_name == "Title":
        return ElementType.HEADING
    if style_name.startswith("List"):
        return ElementType.LIST
    return ElementType.PARAGRAPH


def _table_text(table: Table) -> str:
    rows = [" | ".join(cell.text.strip() for cell in row.cells) for row in table.rows]
    return "\n".join(r for r in rows if r.strip(" |"))


def _para_images(doc: Document, para: Paragraph) -> Iterator[tuple[bytes, str]]:
    for blip in para._p.findall(".//" + qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            part = doc.part.related_parts[rid]
            yield part.blob, part.content_type


def extract_docx(filename: str, data: bytes) -> ExtractedDocument:
    try:
        doc = open_docx(io.BytesIO(data))
    except Exception as exc:
        raise ExtractionError(f"Failed to open DOCX: {exc}") from exc

    elements: list[Element] = []
    images: list[tuple[bytes, str, Location]] = []
    section: str | None = None

    for block_index, block in enumerate(_iter_blocks(doc), start=1):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                el_type = _para_type(block.style.name if block.style else "") # type: ignore
                if el_type is ElementType.HEADING:
                    section = text
                elements.append(
                    Element(
                        text=text,
                        element_type=el_type,
                        location=Location(section=section, block_index=block_index),
                    )
                )
            for blob, mime in _para_images(doc, block):
                images.append((blob, mime, Location(section=section, block_index=block_index)))
        else:
            text = _table_text(block)
            if text:
                elements.append(
                    Element(
                        text=text,
                        element_type=ElementType.TABLE,
                        location=Location(section=section, block_index=block_index),
                    )
                )

    elements.extend(images_to_elements(images))

    if not elements:
        raise ExtractionError("DOCX has no extractable text or images")

    return ExtractedDocument(
        filename=filename,
        mime_type=_MIME,
        format="docx",
        file_hash=hashlib.sha256(data).hexdigest(),
        size_bytes=len(data),
        elements=elements,
        num_units=None,
    )


register_extractor("docx", extract_docx)
