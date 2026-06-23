"""Retriever (hybrid) and reranker (Cohere) factories for RAG search."""

from llama_index.core import VectorStoreIndex
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.retrievers import BaseRetriever

from app.core.config import Settings, get_settings
from app.embeddings.factory import make_embed_model
from app.vectorstore.store import make_vector_store


def make_retriever(settings: Settings | None = None) -> BaseRetriever:
    """Hybrid retriever (vector + full-text) over the existing pgvector store."""
    settings = settings or get_settings()
    index = VectorStoreIndex.from_vector_store(
        make_vector_store(settings),
        embed_model=make_embed_model(settings),
    )
    return index.as_retriever(
        similarity_top_k=settings.retrieve_top_k,
        vector_store_query_mode="hybrid",
        sparse_top_k=settings.retrieve_top_k,
    )


def make_reranker(settings: Settings | None = None) -> BaseNodePostprocessor | None:
    """Cohere reranker (default ON); None if disabled or no API key."""
    settings = settings or get_settings()
    if not settings.rerank_enabled or not settings.cohere_api_key:
        return None

    from llama_index.postprocessor.cohere_rerank import CohereRerank

    return CohereRerank(
        api_key=settings.cohere_api_key,
        model=settings.rerank_model,
        top_n=settings.rerank_top_n,
    )
