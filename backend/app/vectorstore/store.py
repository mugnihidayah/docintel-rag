"""Vector store factory: PGVectorStore over Postgres+pgvector (hybrid search + HNSW cosine)."""

from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url

from app.core.config import Settings, get_settings

_TABLE_NAME = "docintel"  # PGVectorStore creates table "data_docintel"
_HNSW_KWARGS = {
    "hnsw_m": 16,
    "hnsw_ef_construction": 64,
    "hnsw_ef_search": 40,
    "hnsw_dist_method": "vector_cosine_ops",
}


def make_vector_store(settings: Settings | None = None) -> PGVectorStore:
    """Build a hybrid PGVectorStore from the configured database URL."""
    settings = settings or get_settings()
    url = make_url(settings.database_url)
    return PGVectorStore.from_params(
        host=url.host,
        port=str(url.port) if url.port is not None else None,
        database=url.database,
        user=url.username,
        password=url.password,
        table_name=_TABLE_NAME,
        embed_dim=settings.embedding_dim,
        hybrid_search=True,
        text_search_config="simple",
        hnsw_kwargs=_HNSW_KWARGS,
    )
