"""Seed the test corpus: ingest every file in `sample_docs/` like a real upload."""

import asyncio
import hashlib
import mimetypes
import sys
import uuid
from pathlib import Path

from app.core.logging import get_logger, setup_logging
from app.db.models import Document, DocumentStatus
from app.db.session import async_session_maker
from app.documents import repository as repo
from app.ingestion.detector import _EXTENSIONS
from app.rag.indexer import index_document
from app.storage.storage import save_file

logger = get_logger(__name__)

# supported suffixes, derived from the detector so the two never drift
_SUPPORTED = {ext for exts in _EXTENSIONS.values() for ext in exts}

_DEFAULT_DIR = Path(__file__).resolve().parent.parent / "sample_docs"


async def _seed_one(path: Path) -> str:
    """Ingest a single file. Returns a short status string for the summary."""
    data = path.read_bytes()
    if not data:
        return "skipped (empty)"

    file_hash = hashlib.sha256(data).hexdigest()

    async with async_session_maker() as db:
        existing = await repo.get_by_hash(db, file_hash)
        if existing is not None:
            return f"skipped (dedup -> {existing.id})"

        document_id = uuid.uuid4().hex
        storage_path = save_file(document_id, path.name, data)
        doc = await repo.create(
            db,
            Document(
                id=document_id,
                filename=path.name,
                mime_type=mimetypes.guess_type(path.name)[0],
                file_hash=file_hash,
                size_bytes=len(data),
                status=DocumentStatus.indexing,
                storage_path=storage_path,
            ),
        )

        try:
            num_chunks = await asyncio.to_thread(
                index_document, path.name, data, document_id
            )
        except Exception as exc:  # noqa: BLE001 — keep going on the rest of the batch
            logger.exception("Indexing failed for %s", path.name)
            await repo.mark_failed(db, doc, str(exc))
            return f"FAILED ({exc})"

        await repo.mark_indexed(db, doc, num_chunks)
        return f"indexed {num_chunks} chunk(s) -> {document_id}"


async def main() -> int:
    setup_logging()
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_DIR

    if not target.is_dir():
        print(f"Not a directory: {target}")
        return 1

    files = sorted(
        p for p in target.iterdir() if p.is_file() and p.suffix.lower() in _SUPPORTED
    )
    if not files:
        print(f"No supported documents found in {target}")
        print(f"Supported: {', '.join(sorted(_SUPPORTED))}")
        return 1

    print(f"Seeding {len(files)} file(s) from {target}\n")
    failures = 0
    for path in files:
        status = await _seed_one(path)
        if status.startswith("FAILED"):
            failures += 1
        print(f"  {path.name:<40} {status}")

    print(f"\nDone. {len(files) - failures}/{len(files)} indexed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
