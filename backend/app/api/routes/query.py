"""Q&A endpoint: question -> grounded answer + citations."""

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.api.schemas import QueryIn, QueryOut
from app.api.security import rate_limit
from app.rag.query import QueryResult, answer_query

router = APIRouter(tags=["query"], dependencies=[Depends(rate_limit)])


@router.post("/query", response_model=QueryOut)
async def query(payload: QueryIn) -> QueryResult:
    return await run_in_threadpool(answer_query, payload.question)
