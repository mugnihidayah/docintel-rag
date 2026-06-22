"""PDF extractor: text per page + image understanding."""

import hashlib
from collections.abc import Iterator

import fitz

from app.core.errors import ExtractionError
from app.ingestion.detector import register_extractor
from app.ingestion.models import Element, ElementType, ExtractedDocument, Location
from app.ingestion.vision import images_to_elements


def _embedded_images(doc: fitz.Document, page: fitz.Page) -> Iterator[tuple[bytes, str]]:
    for img in page.get_images(full=True):
        info = doc.extract_image(img[0])
        if info:
            yield info["image"], f"image/{info['ext']}"


def extract_pdf(filename: str, data: bytes) -> ExtractedDocument:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise ExtractionError(f"Failed to open PDF: {exc}") from exc

    elements: list[Element] = []
    images: list[tuple[bytes, str, Location]] = []
    try:
        for page_index in range(doc.page_count):
            page = doc[page_index]
            page_no = page_index + 1
            text = page.get_text().strip() # type: ignore
            if text:
                elements.append(
                    Element(
                        text=text,
                        element_type=ElementType.PARAGRAPH,
                        location=Location(page=page_no),
                    )
                )
                images.extend(
                    (blob, mime, Location(page=page_no))
                    for blob, mime in _embedded_images(doc, page)
                )
            elif page.get_images():  # no text but has images -> likely scanned page
                pix = page.get_pixmap(dpi=150)
                images.append((pix.tobytes("png"), "image/png", Location(page=page_no)))
        num_pages = doc.page_count
    finally:
        doc.close()

    elements.extend(images_to_elements(images))

    if not elements:
        raise ExtractionError("PDF has no extractable text or images")

    return ExtractedDocument(
        filename=filename,
        mime_type="application/pdf",
        format="pdf",
        file_hash=hashlib.sha256(data).hexdigest(),
        size_bytes=len(data),
        elements=elements,
        num_units=num_pages,
    )


register_extractor("pdf", extract_pdf)
