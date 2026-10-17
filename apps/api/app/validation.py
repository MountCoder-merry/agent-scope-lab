"""Bounded, side-effect-free import validation."""

from __future__ import annotations

import json
from typing import Any

from .schemas import TraceInput

MAX_BYTES = 1_048_576
MAX_DEPTH = 12
MAX_STRING = 16_384


class TraceValidationError(ValueError):
    def __init__(self, message: str, details: dict[str, Any] | None = None, code: str = "INVALID_TRACE") -> None:
        super().__init__(message)
        self.details = details or {}
        self.code = code


def _walk(value: Any, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise TraceValidationError("payload exceeds maximum nesting depth", code="LIMIT_EXCEEDED")
    if isinstance(value, str) and len(value) > MAX_STRING:
        raise TraceValidationError("field exceeds maximum string length", code="LIMIT_EXCEEDED")
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in {"command", "shell", "exec", "executable", "script"}:
                raise TraceValidationError("executable fields are not accepted", {"field": str(key)})
            _walk(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _walk(child, depth + 1)


def validate_trace_payload(payload: Any) -> TraceInput:
    try:
        raw = payload.get("trace", payload) if isinstance(payload, dict) else payload
        _walk(raw)
        trace = TraceInput.model_validate(raw)
    except TraceValidationError:
        raise
    except Exception as exc:
        raise TraceValidationError("trace does not match the supported schema", {"reason": str(exc)[:256]}) from exc

    span_ids = [span.span_id for span in trace.spans]
    if len(set(span_ids)) != len(span_ids):
        raise TraceValidationError("duplicate span_id", {"field": "spans.span_id"})
    span_set = set(span_ids)
    for span in trace.spans:
        if span.parent_span_id and span.parent_span_id not in span_set:
            raise TraceValidationError("span parent does not exist", {"span_id": span.span_id, "parent_span_id": span.parent_span_id}, "RELATION_INVALID")
    for span in trace.spans:
        visited: set[str] = set()
        current = span
        while current.parent_span_id:
            if current.span_id in visited:
                raise TraceValidationError("cyclic span relation", {"span_id": span.span_id}, "RELATION_INVALID")
            visited.add(current.span_id)
            parent = next(item for item in trace.spans if item.span_id == current.parent_span_id)
            current = parent

    event_ids = [event.event_id for event in trace.events]
    if len(set(event_ids)) != len(event_ids):
        raise TraceValidationError("duplicate event_id", {"field": "events.event_id"})
    if [event.sequence for event in trace.events] != list(range(len(trace.events))):
        raise TraceValidationError("event sequence must be contiguous from zero", {"field": "events.sequence"})
    if any(event.span_id not in span_set for event in trace.events):
        raise TraceValidationError("event references unknown span", {"field": "events.span_id"}, "RELATION_INVALID")
    return trace


def parse_json_bytes(data: bytes) -> TraceInput:
    if len(data) > MAX_BYTES:
        raise TraceValidationError("trace payload exceeds 1 MiB", code="LIMIT_EXCEEDED")
    try:
        payload = json.loads(data)
    except json.JSONDecodeError as exc:
        raise TraceValidationError("request body is not valid JSON", {"line": exc.lineno, "column": exc.colno}) from exc
    return validate_trace_payload(payload)
