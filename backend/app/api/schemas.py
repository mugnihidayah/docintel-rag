"""Pydantic request/response models for the API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: str
    num_chunks: int
    size_bytes: int
    created_at: datetime


class QueryIn(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class CitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str | None
    filename: str | None
    location: dict[str, Any]
    snippet: str
    score: float | None
    score_type: str


class QueryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    answer: str
    citations: list[CitationOut]
    retrieved_chunks: int
    model: str
    latency_ms: int


class ChunkOut(BaseModel):
    text: str
    location: dict[str, Any]


class DocumentChunks(BaseModel):
    document_id: str
    filename: str
    chunks: list[ChunkOut]
