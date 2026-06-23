"""Indexing orchestrator: raw bytes -> extract -> chunk -> embed -> store in pgvector."""

from llama_index.core import StorageContext, VectorStoreIndex

from app.chunking.chunker import chunk_documents
from app.core.config import Settings, get_settings
from app.embeddings.factory import make_embed_model
from app.ingestion.pipeline import extract_to_documents
from app.vectorstore.store import make_vector_store


def index_document(
    filename: str, data: bytes, document_id: str, settings: Settings | None = None
) -> int:
    """Extract, chunk, embed, and store a document's nodes in pgvector. Returns node count."""
    settings = settings or get_settings()
    documents = extract_to_documents(filename, data, document_id)
    nodes = chunk_documents(documents, settings)
    storage_context = StorageContext.from_defaults(vector_store=make_vector_store(settings))
    VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=make_embed_model(settings),
    )
    return len(nodes)
