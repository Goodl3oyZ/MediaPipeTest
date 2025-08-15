# TODO: implement Redis-based rate limiting

from fastapi import HTTPException, Request, status


async def rate_limit_dependency(request: Request) -> None:
    """Placeholder dependency for rate limiting."""
    # In production, track requests per user/IP via Redis
    allow = True
    if not allow:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
