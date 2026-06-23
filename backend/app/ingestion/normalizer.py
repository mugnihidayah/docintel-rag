"""Normalizer: convert an ExtractedDocument into LlamaIndex Documents with source metadata."""

from typing import Any

from llama_index.core import Document

from app.ingestion.models import ExtractedDocument


def to_documents(extracted: ExtractedDocument, document_id: str) -> list[Document]:
    """One LlamaIndex Document per element; metadata carries citation info but is
    excluded from the embedded/LLM text (embeddings stay pure content)."""
    documents: list[Document] = []
    for element in extracted.elements:
        metadata: dict[str, Any] = {
            "document_id": document_id,
            "filename": extracted.filename,
            "format": extracted.format,
            "element_type": element.element_type.value,
            **element.location.as_metadata(),
        }
        keys = list(metadata.keys())
        documents.append(
            Document(
                text=element.text,
                metadata=metadata,
                excluded_embed_metadata_keys=keys,
                excluded_llm_metadata_keys=keys,
            )
        )
    return documents
