"""FastAPI application factory: logging, CORS, request-id, error handling, routers."""

import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import documents, health, query
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import get_logger, request_id_var, setup_logging
from app.observability.tracing import flush, get_tracer

logger = get_logger(__name__)


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("Tracing: %s", "langfuse" if get_tracer() else "disabled")
    yield
    flush()


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()
    app = FastAPI(title="Document Intelligence API", version="0.1.0", lifespan=_lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_id_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        rid = uuid.uuid4().hex[:12]
        token = request_id_var.set(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_var.reset(token)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("AppError %s: %s", exc.code, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "detail": exc.detail}},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "detail": "Internal Server Error"}},
        )

    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(query.router)
    return app


app = create_app()
