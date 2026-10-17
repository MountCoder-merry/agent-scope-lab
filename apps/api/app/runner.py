"""Deterministic LangGraph-backed mock runner with no network/tool side effects."""

from __future__ import annotations

import hashlib
import json
from typing import Any, TypedDict

try:  # LangGraph is optional at import time for minimal API bootstraps.
    from langgraph.graph import END, START, StateGraph
except ImportError:  # pragma: no cover - exercised only in stripped deployments
    END = START = None
    StateGraph = None


class GraphState(TypedDict, total=False):
    scenario_id: str
    strategy_id: str
    failure_mode: str
    retries: int
    status: str
    assertion: str
    virtual_duration_ms: int
    result: dict[str, Any]
    span_diff: list[dict[str, Any]]
    event_diff: list[dict[str, Any]]


SCENARIOS: dict[str, dict[str, Any]] = {
    "tool-timeout": {
        "name": "Tool timeout",
        "description": "A bounded mock tool exceeds its recorded deadline.",
        "strategies": [
            {"id": "bounded-retry", "name": "Bounded retry", "description": "Retry once with a shorter budget."},
            {"id": "fallback-cache", "name": "Use recorded fallback", "description": "Use the last known snapshot and annotate uncertainty."},
        ],
    },
    "invalid-json": {
        "name": "Invalid JSON",
        "description": "A parser receives deterministic malformed structured output.",
        "strategies": [
            {"id": "bounded-retry", "name": "Bounded repair", "description": "Attempt one schema-constrained repair."},
            {"id": "fail-fast", "name": "Fail fast", "description": "Return a clear validation error."},
        ],
    },
    "evidence-conflict": {
        "name": "Evidence conflict",
        "description": "Two recorded sources disagree and require review.",
        "strategies": [
            {"id": "human-review", "name": "Request human review", "description": "Stop before unsupported synthesis."},
            {"id": "prefer-primary", "name": "Prefer primary", "description": "Select the primary source with an audit note."},
        ],
    },
}


def _tool_node(state: GraphState) -> GraphState:
    mode = state.get("failure_mode", "success")
    if mode in {"timeout", "empty", "invalid_json"}:
        return {"status": "failed", "result": {"tool": "mock.weather", "failure_mode": mode}}
    return {"status": "completed", "result": {"tool": "mock.weather", "response": "recorded"}}


def _strategy_node(state: GraphState) -> GraphState:
    scenario = state.get("scenario_id", "tool-timeout")
    strategy = state.get("strategy_id", "bounded-retry")
    mode = state.get("failure_mode", "timeout")
    if scenario == "tool-timeout":
        if strategy == "fallback-cache":
            return {"status": "completed", "retries": 0, "virtual_duration_ms": 1320, "assertion": "weather evidence is annotated as stale", "result": {"fallback": "recorded-weather-snapshot", "uncertainty": True}}
        if strategy == "bounded-retry" and mode == "timeout":
            return {"status": "completed", "retries": 1, "virtual_duration_ms": 2980, "assertion": "second call returns within 2s budget", "result": {"retry": "bounded", "uncertainty": True}}
    if scenario == "invalid-json":
        if strategy == "bounded-retry":
            return {"status": "completed", "retries": 1, "virtual_duration_ms": 420, "assertion": "repaired output validates against schema", "result": {"repair": "schema-constrained"}}
        return {"status": "failed", "retries": 0, "virtual_duration_ms": 220, "assertion": "malformed output is rejected", "result": {"error_code": "INVALID_JSON"}}
    if scenario == "evidence-conflict":
        if strategy == "prefer-primary":
            return {"status": "completed", "retries": 0, "virtual_duration_ms": 950, "assertion": "primary source selected with audit note", "result": {"selected": "primary", "review_required": True}}
        return {"status": "completed", "retries": 0, "virtual_duration_ms": 930, "assertion": "conflict is escalated to human review", "result": {"review_required": True}}
    return {"status": "failed", "retries": 0, "virtual_duration_ms": 0, "assertion": "unknown scenario", "result": {"error_code": "UNKNOWN_SCENARIO"}}


def _diff_node(state: GraphState) -> GraphState:
    result = state.get("result", {})
    status = state.get("status", "failed")
    return {"span_diff": [{"span_id": "mock.strategy", "change": "added", "status": status}], "event_diff": [{"sequence": 0, "change": "strategy.completed", "payload": result}]}


def run_mock(*, scenario_id: str, strategy_id: str, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run a deterministic graph; input is treated as data and never executed."""
    if scenario_id not in SCENARIOS:
        raise ValueError("unknown scenario")
    if not any(item["id"] == strategy_id for item in SCENARIOS[scenario_id]["strategies"]):
        raise ValueError("strategy is not available for scenario")
    input_data = input_data or {}
    state: GraphState = {"scenario_id": scenario_id, "strategy_id": strategy_id, "failure_mode": str(input_data.get("failure_mode", "timeout")), "retries": 0}
    if StateGraph is not None:
        graph = StateGraph(GraphState)
        graph.add_node("mock_tool", _tool_node)
        graph.add_node("strategy", _strategy_node)
        graph.add_node("diff", _diff_node)
        graph.add_edge(START, "mock_tool")
        graph.add_edge("mock_tool", "strategy")
        graph.add_edge("strategy", "diff")
        graph.add_edge("diff", END)
        result = graph.compile().invoke(state)
    else:  # A small fallback keeps the API bootable if an operator omits extras.
        result = {**state, **_tool_node(state)}
        result.update(_strategy_node(result))
        result.update(_diff_node(result))
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"), default=str)
    result["input_hash"] = hashlib.sha256(json.dumps(input_data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    result["result_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    return dict(result)
