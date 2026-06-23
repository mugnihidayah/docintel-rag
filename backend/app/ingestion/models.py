"""Normalized extraction model shared by all format extractors"""

from dataclasses import asdict, dataclass, field
from enum import StrEnum


class ElementType(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TABLE = "table"
    LIST = "list"
    SLIDE_TEXT = "slide_text"
    NOTES = "notes"
    CELL_BLOCK = "cell_block"
    IMAGE = "image"


@dataclass(slots=True)
class Location:
    """Where an element lives in its source (only relevant fields are set)."""

    page: int | None = None
    slide: int | None = None
    sheet: str | None = None
    section: str | None = None
    block_index: int | None = None
    row_start: int | None = None
    row_end: int | None = None

    def as_metadata(self) -> dict[str, int | str]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass(slots=True)
class Element:
    text: str
    element_type: ElementType
    location: Location


@dataclass
class ExtractedDocument:
    """Uniform output every extractor produces, regardless of source format"""

    filename: str
    mime_type: str
    format: str
    file_hash: str
    size_bytes: int
    elements: list[Element] = field(default_factory=list)
    num_units: int | None = None
