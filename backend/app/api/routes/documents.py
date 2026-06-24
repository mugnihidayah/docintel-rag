"""Document ingestion endpoint: upload -> store -> index -> persist status."""

import hashlib
import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.schemas import ChunkOut, DocumentChunks, DocumentOut
from app.api.security import rate_limit, require_api_key
from app.core.config import get_settings
from app.core.errors import ExtractionError, NotFoundError, PayloadTooLargeError
from app.core.logging import get_logger
from app.db.models import Document, DocumentStatus
from app.documents import repository as repo
from app.rag.indexer import index_document
from app.storage.storage import delete_file, save_file

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(rate_limit)])


@router.post(
    "", response_model=DocumentOut, status_code=201, dependencies=[Depends(require_api_key)]
)  # noqa: E501
async def upload_document(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
) -> Document:
    settings = get_settings()
    data = await file.read()

    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise PayloadTooLargeError(f"File exceeds {settings.max_upload_mb} MB limit")

    file_hash = hashlib.sha256(data).hexdigest()
    existing = await repo.get_by_hash(db, file_hash)
    if existing is not None:
        return existing  # dedup: identical file already ingested

    filename = file.filename or "upload"
    document_id = uuid.uuid4().hex
    storage_path = save_file(document_id, filename, data)

    doc = await repo.create(
        db,
        Document(
            id=document_id,
            filename=filename,
            mime_type=file.content_type,
            file_hash=file_hash,
            size_bytes=len(data),
            status=DocumentStatus.indexing,
            storage_path=storage_path,
        ),
    )

    try:
        num_chunks = await run_in_threadpool(index_document, filename, data, document_id)
    except Exception as exc:
        logger.exception("Indexing failed for %s", document_id)
        await repo.mark_failed(db, doc, str(exc))
        raise ExtractionError(f"Failed to index document: {exc}") from exc

    return await repo.mark_indexed(db, doc, num_chunks)


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)
) -> Sequence[Document]:
    return await repo.list_documents(db, limit=limit, offset=offset)


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)) -> Document:
    doc = await repo.get(db, document_id)
    if doc is None:
        raise NotFoundError(f"Document {document_id} not found")
    return doc


@router.get("/{document_id}/chunks", response_model=DocumentChunks)
async def get_document_chunks(
    document_id: str, db: AsyncSession = Depends(get_db)
) -> DocumentChunks:
    doc = await repo.get(db, document_id)
    if doc is None:
        raise NotFoundError(f"Document {document_id} not found")
    chunks = await repo.get_chunks(db, document_id)
    return DocumentChunks(
        document_id=document_id,
        filename=doc.filename,
        chunks=[ChunkOut.model_validate(c) for c in chunks],
    )


@router.delete("/{document_id}", status_code=204, dependencies=[Depends(require_api_key)])
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)) -> None:
    doc = await repo.get(db, document_id)
    if doc is None:
        raise NotFoundError(f"Document {document_id} not found")
    await repo.delete(db, doc)
    delete_file(document_id)
