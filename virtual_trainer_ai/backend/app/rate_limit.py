"""Simple Redis-based rate limiting dependency."""

from datetime import datetime

import redis
from fastapi import HTTPException, Request, status

from .config import settings

_redis = redis.from_url(settings.redis_url)


async def rate_limit_dependency(request: Request, limit: int = 100, window_seconds: int = 60) -> None:
    identifier = request.client.host if request.client else "unknown"
    key = f"rl:{identifier}"
    count = _redis.incr(key)
    if count == 1:
        _redis.expire(key, window_seconds)
    if count > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
