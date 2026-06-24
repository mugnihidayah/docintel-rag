"""Optional Langfuse tracing for the RAG pipeline (no-op unless configured)."""

from functools import lru_cache
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_tracer() -> Any | None:
    """Return a configured Langfuse client, or None when tracing is disabled."""
    settings = get_settings()
    if not settings.langfuse_enabled:
        return None
    try:
        from langfuse import Langfuse

        client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host or "https://cloud.langfuse.com",
        )
    except Exception as exc:  # pragma: no cover - external dependency / network
        logger.warning("Langfuse init failed, tracing disabled: %s", exc)
        return None

    # Auto-instrument LlamaIndex (OpenInference/OTEL) so retrieval + LLM calls are
    # captured and nested under our query span — the recommended approach for
    # framework apps (vs. hand-rolled spans for every call).
    try:
        from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

        LlamaIndexInstrumentor().instrument()
        logger.info("Langfuse tracing + LlamaIndex auto-instrumentation enabled")
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("LlamaIndex instrumentation unavailable: %s", exc)

    return client


def flush() -> None:
    """Flush pending traces; safe to call on shutdown."""
    client = get_tracer()
    if client is not None:
        client.flush()
