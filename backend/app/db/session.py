"""Async engine + session factory for request-scoped DB access."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
