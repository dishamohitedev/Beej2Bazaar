"""
Rate limiting for sensitive endpoints (OTP request/verify), to prevent SMS
bombing and OTP brute-forcing.

This in-memory limiter is fine for a single-instance dev/staging deploy.
Once you scale to multiple backend instances on Render, swap the `_hits`
dict for a Redis INCR+EXPIRE pattern (interface stays identical).
"""
import time
from collections import defaultdict
from fastapi import HTTPException, status

_hits: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    now = time.time()
    window_start = now - window_seconds
    _hits[key] = [t for t in _hits[key] if t > window_start]

    if len(_hits[key]) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Try again in {window_seconds} seconds.",
        )
    _hits[key].append(now)
