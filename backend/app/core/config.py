from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    app_env: str = "dev"  # dev | prod

    # Database
    database_url: str = "postgresql+asyncpg://docintel:docintel@localhost:5432/docintel"

    # LLM
    llm_api_key: str | None = None
    llm_model: str = "llama-3.3-70b-versatile"
    llm_base_url: str | None = None
    llm_provider: str = "groq"

    # Embedding
    embedding_provider: str = "jina"
    embedding_api_key: str | None = None
    embedding_model: str = "jina-embeddings-v5-text-small"
    embedding_base_url: str | None = None
    embedding_dim: int = 1024

    # Reranker
    rerank_enabled: bool = True
    cohere_api_key: str | None = None
    rerank_model: str = "rerank-multilingual-v3.0"
    retrieve_top_k: int = 30
    rerank_top_n: int = 10
    rerank_timeout_s: float = 5.0

    # Retrieval Mode
    retrieval_mode: str = "hybrid"  # hybrid | fusion

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    api_key: str | None = None
    rate_limit_per_min: int = 0

    # upload / storage
    upload_dir: str = "data/uploads"
    max_upload_mb: int = 25
    max_batch_files: int = 20

    # eval
    eval_judge_model: str = "openai/gpt-oss-120b"

    # langfuse
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    # accept both LANGFUSE_HOST and Langfuse's own LANGFUSE_BASE_URL naming
    langfuse_host: str | None = Field(
        default=None, validation_alias=AliasChoices("langfuse_host", "langfuse_base_url")
    )

    # Vision
    vision_enabled: bool = True
    vision_api_key: str | None = None
    vision_base_url: str = "https://api.groq.com/openai/v1"
    vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    vision_max_images: int = 10
    vision_min_image_kb: int = 20
    vision_timeout_s: float = 30.0

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)

    @property
    def is_prod(self) -> bool:
        return self.app_env.lower() == "prod"

    @property
    def is_dev(self) -> bool:
        return not self.is_prod

    @property
    def vision_key(self) -> str | None:
        return self.vision_api_key or self.llm_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
