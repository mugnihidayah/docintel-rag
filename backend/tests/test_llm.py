from types import SimpleNamespace

import pytest

from app.llm.factory import make_llm
from app.llm.prompts import GROUNDING_QA_TEMPLATE


def _settings(**kw: object) -> SimpleNamespace:
    base = {
        "llm_provider": "groq",
        "llm_model": "llama-3.3-70b-versatile",
        "llm_api_key": "test-key",
    }
    base.update(kw)
    return SimpleNamespace(**base)


def test_make_llm_groq() -> None:
    from llama_index.llms.groq import Groq

    assert isinstance(make_llm(_settings()), Groq)


def test_make_llm_unknown_provider_raises() -> None:
    with pytest.raises(ValueError):
        make_llm(_settings(llm_provider="unknown"))


def test_grounding_template_has_guardrails() -> None:
    t = GROUNDING_QA_TEMPLATE.template
    assert "{context_str}" in t and "{query_str}" in t
    assert "Tidak ditemukan" in t
