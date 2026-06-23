"""Ingestion entry point: bytes -> LlamaIndex Documents (detect -> route -> extract -> normalize)"""

from llama_index.core import Document

from app.ingestion.detector import detect_format, get_extractor
from app.ingestion.normalizer import to_documents


def extract_to_documents(filename: str, data: bytes, document_id: str) -> list[Document]:
    fmt = detect_format(filename, data)
    extractor = get_extractor(fmt)
    extracted = extractor(filename, data)
    return to_documents(extracted, document_id)
