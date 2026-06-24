"""API key authentication and simple in-memory rate limiting."""

import time
from collections import deque

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import RateLimitedError, UnauthorizedError

_hits: dict[str, deque[float]] = {}


async def require_api_key(request: Request) -> None:
    """Require a valid X-API-Key header when one is configured (no-op in dev)."""
    api_key = get_settings().api_key
    if not api_key:
        return
    if request.headers.get("X-API-Key") != api_key:
        raise UnauthorizedError("Invalid or missing API key")


async def rate_limit(request: Request) -> None:
    """Sliding 60s window per client IP. Disabled when RATE_LIMIT_PER_MIN <= 0."""
    limit = get_settings().rate_limit_per_min
    if limit <= 0:
        return
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _hits.setdefault(client, deque())
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= limit:
        raise RateLimitedError("Rate limit exceeded, try again later")
    window.append(now)
