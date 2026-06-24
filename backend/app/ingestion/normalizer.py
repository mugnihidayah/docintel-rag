"""Normalizer: convert an ExtractedDocument into LlamaIndex Documents with source metadata.

Consecutive elements are grouped into coherent sections (a heading plus the content that
follows it) so retrieval sees self-contained chunks instead of isolated one-line fragments.
Grouping breaks at headings, at structural boundaries (page/slide/sheet), and at a character
budget; citation metadata is anchored to the section's first element.
"""

import re
from typing import Any

from llama_index.core import Document

from app.ingestion.models import Element, ElementType, ExtractedDocument

# A line like "6. Penilaian" or "3.1. Sub-bagian" — a numbered section heading.
_HEADING_RE = re.compile(r"^\s*\d+(\.\d+)*\.\s+\S")
_MAX_GROUP_CHARS = 1200


def _is_heading(element: Element) -> bool:
    return element.element_type == ElementType.HEADING or bool(_HEADING_RE.match(element.text))


def _structural_key(element: Element) -> tuple[object, object, object]:
    loc = element.location
    return (loc.page, loc.slide, loc.sheet)


def _group_elements(elements: list[Element]) -> list[list[Element]]:
    """A new section starts at a heading, when the structural unit (page/slide/sheet)
    changes, or when the running character budget would be exceeded."""
    groups: list[list[Element]] = []
    current: list[Element] = []
    chars = 0
    for el in elements:
        starts_new = bool(current) and (
            _is_heading(el)
            or _structural_key(el) != _structural_key(current[0])
            or chars + len(el.text) > _MAX_GROUP_CHARS
        )
        if starts_new:
            groups.append(current)
            current = []
            chars = 0
        current.append(el)
        chars += len(el.text)
    if current:
        groups.append(current)
    return groups


def to_documents(extracted: ExtractedDocument, document_id: str) -> list[Document]:
    """One LlamaIndex Document per *section* (grouped elements). Metadata carries citation
    info (anchored to the section's first element) but is excluded from the embedded/LLM
    text so embeddings stay pure content.

    Note: PGVectorStore reserves the 'document_id' metadata key and overwrites it (in the
    stored column) with each node's ref_doc_id. We therefore also store an untouched
    'source_id' mirror, which is what we filter on to fetch/delete by file."""
    documents: list[Document] = []
    for group in _group_elements(extracted.elements):
        text = "\n".join(el.text for el in group if el.text).strip()
        if not text:
            continue
        head = group[0]
        metadata: dict[str, Any] = {
            "document_id": document_id,
            "source_id": document_id,
            "filename": extracted.filename,
            "format": extracted.format,
            "element_type": head.element_type.value,
            **head.location.as_metadata(),
        }
        keys = list(metadata.keys())
        documents.append(
            Document(
                text=text,
                metadata=metadata,
                excluded_embed_metadata_keys=keys,
                excluded_llm_metadata_keys=keys,
            )
        )
    return documents
