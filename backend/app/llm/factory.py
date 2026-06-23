"""LLM factory: build a pluggable LLM from settings (default Groq)."""

from llama_index.core.llms import LLM

from app.core.config import Settings, get_settings


def make_llm(settings: Settings | None = None) -> LLM:
    """Return an LLM based on the configured provider."""
    settings = settings or get_settings()
    provider = settings.llm_provider.lower()

    if provider == "groq":
        from llama_index.llms.groq import Groq

        return Groq(model=settings.llm_model, api_key=settings.llm_api_key, temperature=0)

    raise ValueError(
        f"Unsupported LLM provider: {provider!r} "
        "(install llama-index-llms-<provider> and add a branch here)"
    )
