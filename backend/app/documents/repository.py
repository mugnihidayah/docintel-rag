"""Async CRUD helpers for the documents table."""

from collections.abc import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentStatus


async def get_by_hash(db: AsyncSession, file_hash: str) -> Document | None:
    result = await db.execute(select(Document).where(Document.file_hash == file_hash))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, doc: Document) -> Document:
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def mark_indexed(db: AsyncSession, doc: Document, num_chunks: int) -> Document:
    doc.status = DocumentStatus.indexed
    doc.num_chunks = num_chunks
    await db.commit()
    await db.refresh(doc)
    return doc


async def mark_failed(db: AsyncSession, doc: Document, error: str) -> Document:
    doc.status = DocumentStatus.failed
    doc.error = error[:1000]
    await db.commit()
    await db.refresh(doc)
    return doc


async def list_documents(db: AsyncSession, limit: int = 100, offset: int = 0) -> Sequence[Document]:
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all()


async def get(db: AsyncSession, document_id: str) -> Document | None:
    return await db.get(Document, document_id)


async def delete(db: AsyncSession, doc: Document) -> None:
    # Remove the document's vector nodes first, then the relational row.
    await db.execute(
        text("DELETE FROM data_docintel WHERE metadata_->>'document_id' = :doc_id"),
        {"doc_id": doc.id},
    )
    await db.delete(doc)
    await db.commit()
