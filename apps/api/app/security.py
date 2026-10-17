"""Small, dependency-free request guards for the self-hosted API.

The public Demo never exposes this service.  These guards still make a local
deployment fail closed for oversized writes and provide a bounded in-process
write rate limit.  Operators running multiple workers should place a shared
proxy/rate limiter in front of the API as documented in the deployment guide.
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict, deque
from threading import Lock
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

MAX_REQUEST_BYTES = 1_048_576
WRITE_WINDOW_SECONDS = 60.0
DEFAULT_WRITE_LIMIT = 30

logger = logging.getLogger("agentscope.api.access")
logger.setLevel(logging.INFO)


def _configured_write_limit() -> int:
    raw = os.getenv("AGENTSCOPE_WRITE_RATE_LIMIT", str(DEFAULT_WRITE_LIMIT))
    try:
        return max(1, min(int(raw), 10_000))
    except ValueError:
        return DEFAULT_WRITE_LIMIT


class SlidingWindowRateLimiter:
    """Thread-safe bounded sliding-window limiter keyed by client identity."""

    def __init__(self, limit: int = DEFAULT_WRITE_LIMIT, window_seconds: float = WRITE_WINDOW_SECONDS) -> None:
        self.limit = max(1, limit)
        self.window_seconds = max(1.0, window_seconds)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits[key]
            cutoff = current - self.window_seconds
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(current)
            if len(self._hits) > 2048:
                stale = [name for name, values in self._hits.items() if not values or values[-1] <= cutoff]
                for name in stale:
                    self._hits.pop(name, None)
            return True


write_limiter = SlidingWindowRateLimiter(limit=_configured_write_limit())


def _client_key(request: Request) -> str:
    # Do not trust forwarded headers by default; a reverse proxy can normalize
    # client identity before forwarding if it is explicitly configured.
    return request.client.host if request.client else "unknown"


def _error_response(code: str, message: str, status_code: int, details: dict[str, object] | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message, "details": details or {}}})


class RequestGuardMiddleware(BaseHTTPMiddleware):
    """Enforce write limits and emit metadata-only JSON access logs."""

    async def dispatch(self, request: Request, call_next) -> Response:
        started = time.perf_counter()
        request_id = uuid4().hex
        response: Response
        if request.url.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH"}:
            content_length = request.headers.get("content-length")
            try:
                too_large = content_length is not None and int(content_length) > MAX_REQUEST_BYTES
            except ValueError:
                too_large = True
            if too_large:
                response = _error_response("LIMIT_EXCEEDED", "request body exceeds 1 MiB", 413)
            elif not write_limiter.allow(_client_key(request)):
                response = _error_response("RATE_LIMITED", "write rate limit exceeded", 429, {"retry_after_seconds": int(WRITE_WINDOW_SECONDS)})
                response.headers["Retry-After"] = str(int(WRITE_WINDOW_SECONDS))
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(json.dumps({"request_id": request_id, "method": request.method, "path": request.url.path, "status": response.status_code, "duration_ms": duration_ms, "client": _client_key(request)}, separators=(",", ":")))
        return response
