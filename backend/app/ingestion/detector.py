"""format detection and extractor routing"""

from pathlib import Path
from typing import Protocol

import magic

from app.core.errors import UnsupportedFormatError, ValidationError
from app.ingestion.models import ExtractedDocument

_EXTENSIONS: dict[str, set[str]] = {
    "pdf": {".pdf"},
    "docx": {".docx"},
    "pptx": {".pptx"},
    "xlsx": {".xlsx"},
    "csv": {".csv"},
    "txt": {".txt"},
}

# coarse content from libmagic, used to cross check the extension
_PDF_MIMES = {"application/pdf"}
_TEXT_MIMES = {"text/plain", "text/csv", "application/csv"}
_ZIP_MIMES = {
    "application/zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

_FAMILY: dict[str, set[str]] = {
    "pdf": _PDF_MIMES,
    "docx": _ZIP_MIMES,
    "pptx": _ZIP_MIMES,
    "xlsx": _ZIP_MIMES,
    "csv": _TEXT_MIMES,
    "txt": _TEXT_MIMES,
}


def detect_format(filename: str, data: bytes) -> str:
    """detect a supported format from extension + magic bytes, or raise"""
    if not data:
        raise ValidationError("Empty file")
    ext = Path(filename).suffix.lower()
    fmt = next((f for f, exts in _EXTENSIONS.items() if ext in exts), None)
    if fmt is None:
        raise UnsupportedFormatError(f"Unsupported file extension: {ext or '(none)'}")

    mime = magic.from_buffer(data, mime=True)
    if mime not in _FAMILY[fmt]:
        raise UnsupportedFormatError(f"Content does not match extension '{ext}' (detected: {mime})")
    return fmt


class Extractor(Protocol):
    def __call__(self, filename: str, data: bytes) -> ExtractedDocument: ...


_EXTRACTORS: dict[str, Extractor] = {}


def register_extractor(fmt: str, extractor: Extractor) -> None:
    _EXTRACTORS[fmt] = extractor


def get_extractor(fmt: str) -> Extractor:
    extractor = _EXTRACTORS.get(fmt)
    if extractor is None:
        raise UnsupportedFormatError(f"No extractor registered for format: {fmt}")
    return extractor
