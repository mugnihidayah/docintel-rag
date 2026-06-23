"""End-to-end demo: ingest a file, then ask a question over it.

Uses real services (embedding + LLM APIs + pgvector), so it needs a populated
`.env` and a running database. Meant for manual/demo runs, not the test suite.

Usage (from backend/):
    uv run python -m scripts.ask path/to/file.pdf "Your question?"
"""

import sys
import uuid
from pathlib import Path

from app.core.logging import setup_logging
from app.rag.indexer import index_document
from app.rag.query import answer_query


def main() -> int:
    if len(sys.argv) != 3:
        print('Usage: python -m scripts.ask <file> "<question>"')
        return 1

    setup_logging()
    path, question = Path(sys.argv[1]), sys.argv[2]
    document_id = f"demo-{uuid.uuid4().hex[:8]}"

    nodes = index_document(path.name, path.read_bytes(), document_id)
    print(f"\nIndexed {nodes} node(s) from {path.name} (document_id={document_id})\n")

    result = answer_query(question)
    print("=" * 60)
    print(f"Q: {question}")
    print(f"A: {result.answer}")
    print(f"   {result.model} | {result.latency_ms} ms | {result.retrieved_chunks} chunks")
    print("-" * 60)
    for i, c in enumerate(result.citations, 1):
        loc = ", ".join(f"{k}={v}" for k, v in c.location.items())
        print(f"  [{i}] {c.filename} ({loc}) score={c.score} [{c.score_type}]")
        print(f'      "{c.snippet}"')
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
