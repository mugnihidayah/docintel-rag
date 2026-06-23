"""Embedding factory: build a pluggable embedding model from settings"""

from llama_index.core.embeddings import BaseEmbedding

from app.core.config import Settings, get_settings


def make_embed_model(settings: Settings | None = None) -> BaseEmbedding:
    """Return an embedding model based on the configured provider."""
    settings = settings or get_settings()
    provider = settings.embedding_provider.lower()

    if provider == "jina":
        from llama_index.embeddings.jinaai import JinaEmbedding

        return JinaEmbedding(
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            task="retrieval.passage",
        )

    raise ValueError(
        f"Unsupported embedding provider: {provider!r} "
        "(install llama-index-embeddings-<provider> and add a branch here)"
    )
