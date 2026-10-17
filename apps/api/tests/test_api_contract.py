from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.runner import run_mock


def trace_payload(trace_id: str) -> dict:
    return {
        "traceId": trace_id,
        "schemaVersion": "1.0",
        "sourceFramework": "synthetic",
        "scenario": "tool-timeout",
        "title": "API contract test",
        "summary": "recorded",
        "status": "failed",
        "startedAt": "10:00:00",
        "durationMs": 10,
        "spans": [
            {"spanId": "root", "kind": "agent", "name": "root", "status": "error", "durationMs": 10},
            {"spanId": "tool", "parentSpanId": "root", "kind": "tool", "name": "tool", "status": "error", "durationMs": 10},
        ],
        "events": [
            {"eventId": "e0", "sequence": 0, "spanId": "root", "type": "span.started"},
            {"eventId": "e1", "sequence": 1, "spanId": "tool", "type": "tool.failed"},
        ],
    }


def test_trace_import_and_query() -> None:
    client = TestClient(app)
    trace_id = f"contract_test_trace_{uuid4().hex}"
    response = client.post("/api/v1/traces/import", json=trace_payload(trace_id))
    assert response.status_code == 201
    detail = client.get(f"/api/v1/traces/{trace_id}")
    assert detail.status_code == 200
    assert detail.json()["trace_id"] == trace_id
    assert all(item["trace_id"] == trace_id for item in detail.json()["spans"])
    assert client.get(f"/api/v1/traces/{trace_id}/events").json()[0]["sequence"] == 0


def test_import_relationship_failure_is_rejected() -> None:
    client = TestClient(app)
    payload = trace_payload("contract_invalid_relation")
    payload["spans"][1]["parentSpanId"] = "missing"
    response = client.post("/api/v1/traces/import", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "RELATION_INVALID"
    assert client.get("/api/v1/traces/contract_invalid_relation").status_code == 404


def test_mock_runner_is_stable_and_side_effect_free() -> None:
    first = run_mock(scenario_id="tool-timeout", strategy_id="bounded-retry")
    second = run_mock(scenario_id="tool-timeout", strategy_id="bounded-retry")
    assert first == second
    assert first["status"] == "completed"
    assert first["retries"] == 1
