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
    with TestClient(app) as client:
        trace_id = f"contract_test_trace_{uuid4().hex}"
        response = client.post("/api/v1/traces/import", json=trace_payload(trace_id))
        assert response.status_code == 201
        detail = client.get(f"/api/v1/traces/{trace_id}")
        assert detail.status_code == 200
        assert detail.json()["trace_id"] == trace_id
        assert all(item["trace_id"] == trace_id for item in detail.json()["spans"])
        assert client.get(f"/api/v1/traces/{trace_id}/events").json()[0]["sequence"] == 0


def test_import_relationship_failure_is_rejected() -> None:
    with TestClient(app) as client:
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


def test_scenarios_and_experiment_lifecycle() -> None:
    with TestClient(app) as client:
        scenarios = client.get("/api/v1/scenarios")
        assert scenarios.status_code == 200
        assert {item["scenario_id"] for item in scenarios.json()} == {"tool-timeout", "invalid-json", "evidence-conflict"}

        created = client.post(
            "/api/v1/experiments",
            json={"scenarioId": "invalid-json", "strategyId": "fail-fast", "input": {"failure_mode": "invalid_json"}},
        )
        assert created.status_code == 201
        experiment_id = created.json()["experiment_id"]
        assert created.json()["status"] == "created"

        run = client.post(f"/api/v1/experiments/{experiment_id}/run")
        assert run.status_code == 200
        assert run.json()["status"] == "failed"
        assert run.json()["assertion"] == "malformed output is rejected"
        assert run.json()["event_diff"]

        fetched = client.get(f"/api/v1/experiments/{experiment_id}")
        assert fetched.status_code == 200
        assert fetched.json()["result"]["error_code"] == "INVALID_JSON"

        input_sensitive = client.post(
            "/api/v1/experiments",
            json={"scenarioId": "tool-timeout", "strategyId": "bounded-retry", "input": {"failure_mode": "empty"}},
        )
        assert input_sensitive.status_code == 201
        second_run = client.post(f"/api/v1/experiments/{input_sensitive.json()['experiment_id']}/run")
        assert second_run.status_code == 200
        assert second_run.json()["status"] == "failed"
