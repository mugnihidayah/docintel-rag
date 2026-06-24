"""RAG query orchestrator: retrieve -> rerank (with fallback) -> grounded answer -> citations."""

import time
from dataclasses import dataclass

from llama_index.core.schema import NodeWithScore

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.llm.factory import make_llm
from app.llm.prompts import GROUNDING_QA_TEMPLATE
from app.observability.tracing import get_tracer
from app.retrieval.retriever import make_reranker, make_retriever

logger = get_logger(__name__)

_LOCATION_KEYS = ("page", "slide", "sheet", "section", "block_index", "row_start", "row_end")
_NOT_FOUND = "Tidak ditemukan dalam dokumen."


@dataclass(slots=True)
class Citation:
    document_id: str | None
    filename: str | None
    location: dict[str, object]
    snippet: str
    score: float | None
    score_type: str


@dataclass(slots=True)
class QueryResult:
    answer: str
    citations: list[Citation]
    retrieved_chunks: int
    model: str
    latency_ms: int


def _build_citations(nodes: list[NodeWithScore], score_type: str) -> list[Citation]:
    citations: list[Citation] = []
    for nws in nodes:
        meta = nws.node.metadata
        citations.append(
            Citation(
                document_id=meta.get("document_id"),
                filename=meta.get("filename"),
                location={k: meta[k] for k in _LOCATION_KEYS if k in meta},
                snippet=nws.node.get_content()[:200].strip(),
                score=nws.score,
                score_type=score_type,
            )
        )
    return citations


def _run_query(question: str, settings: Settings | None = None) -> QueryResult:
    settings = settings or get_settings()
    started = time.perf_counter()
    model = f"{settings.llm_provider}:{settings.llm_model}"

    nodes = make_retriever(settings).retrieve(question)
    if not nodes:
        elapsed = int((time.perf_counter() - started) * 1000)
        return QueryResult(_NOT_FOUND, [], 0, model, elapsed)

    score_type = "hybrid"
    reranker = make_reranker(settings)
    if reranker is not None:
        try:
            nodes = reranker.postprocess_nodes(nodes, query_str=question)
            score_type = "rerank"
        except Exception as exc:
            logger.warning("Rerank failed, using retriever order: %s", exc)
            nodes = nodes[: settings.rerank_top_n]

    context = "\n\n".join(nws.node.get_content() for nws in nodes)
    prompt = GROUNDING_QA_TEMPLATE.format(context_str=context, query_str=question)
    answer = str(make_llm(settings).complete(prompt)).strip()

    elapsed = int((time.perf_counter() - started) * 1000)
    return QueryResult(answer, _build_citations(nodes, score_type), len(nodes), model, elapsed)


def answer_query(question: str, settings: Settings | None = None) -> QueryResult:
    """Run the query, recording a Langfuse trace when observability is enabled."""
    tracer = get_tracer()
    if tracer is None:
        return _run_query(question, settings)
    with tracer.start_as_current_observation(name="rag_query") as span:
        result = _run_query(question, settings)
        span.update(
            input={"question": question},
            output={"answer": result.answer},
            metadata={
                "model": result.model,
                "latency_ms": result.latency_ms,
                "retrieved_chunks": result.retrieved_chunks,
                "citations": len(result.citations),
            },
        )
        return result
