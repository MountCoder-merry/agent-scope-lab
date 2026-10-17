import logging

from fastapi.testclient import TestClient

from app.main import app
from app.security import SlidingWindowRateLimiter, write_limiter


def test_sliding_window_limiter_is_bounded_and_expires() -> None:
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=10)
    assert limiter.allow("client", now=100)
    assert limiter.allow("client", now=101)
    assert not limiter.allow("client", now=102)
    assert limiter.allow("client", now=111)


def test_oversized_write_is_rejected_and_request_id_is_returned(caplog) -> None:
    with TestClient(app) as client, caplog.at_level(logging.INFO, logger="agentscope.api.access"):
        response = client.post(
            "/api/v1/traces/import",
            content=b"{}",
            headers={"content-length": "1048577"},
        )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "LIMIT_EXCEEDED"
    assert response.headers["X-Request-ID"]
    assert '"path":"/api/v1/traces/import"' in caplog.text


def test_rate_limit_response_has_retry_after() -> None:
    original_limit = write_limiter.limit
    original_hits = write_limiter._hits.copy()
    try:
        write_limiter.limit = 1
        write_limiter._hits.clear()
        with TestClient(app) as client:
            assert client.post("/api/v1/experiments", json={"scenarioId": "invalid-json", "strategyId": "fail-fast"}).status_code == 201
            response = client.post("/api/v1/experiments", json={"scenarioId": "invalid-json", "strategyId": "fail-fast"})
        assert response.status_code == 429
        assert response.headers["Retry-After"] == "60"
        assert response.json()["error"]["code"] == "RATE_LIMITED"
    finally:
        write_limiter.limit = original_limit
        write_limiter._hits.clear()
        write_limiter._hits.update(original_hits)
