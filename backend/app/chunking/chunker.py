"""Chunker: split LlamaIndex Documents into nodes; structure-aware via per-element documents."""

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode

from app.core.config import Settings, get_settings


def make_node_parser(settings: Settings | None = None) -> SentenceSplitter:
    settings = settings or get_settings()
    return SentenceSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def chunk_documents(documents: list[Document], settings: Settings | None = None) -> list[BaseNode]:
    """Split documents into nodes; each node inherits its source document's metadata."""
    return make_node_parser(settings).get_nodes_from_documents(documents)
