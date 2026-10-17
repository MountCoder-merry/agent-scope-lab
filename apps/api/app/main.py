"""AgentScope API: trace persistence, validated imports and deterministic experiments."""

from __future__ import annotations

import hashlib
import json
from contextlib import asynccontextmanager
from datetime import datetime, time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import get_db, init_db
from .models import Evaluation, Experiment, Project, Span, Trace, TraceEvent
from .runner import SCENARIOS, run_mock
from .schemas import (
    EventResponse,
    ExperimentCreate,
    ExperimentResponse,
    HealthResponse,
    PaginatedTraces,
    ProjectResponse,
    ScenarioResponse,
    SpanResponse,
    TraceInput,
    TraceResponse,
    TraceSummary,
)
from .security import RequestGuardMiddleware
from .validation import TraceValidationError, parse_json_bytes


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AgentScope API", version="0.2.0", docs_url="/docs", lifespan=lifespan)
app.add_middleware(RequestGuardMiddleware)


@app.exception_handler(TraceValidationError)
def trace_error_handler(_: Request, exc: TraceValidationError) -> JSONResponse:
    return JSONResponse(status_code=413 if exc.code == "LIMIT_EXCEEDED" else 422, content={"error": {"code": exc.code, "message": str(exc), "details": exc.details}})


@app.exception_handler(RequestValidationError)
def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": {"code": "INVALID_REQUEST", "message": "request validation failed", "details": {"errors": exc.errors()}}})


def _error(code: str, message: str, details: dict[str, Any] | None = None, http_status: int = 400) -> HTTPException:
    return HTTPException(status_code=http_status, detail={"error": {"code": code, "message": message, "details": details or {}}})


@app.exception_handler(HTTPException)
def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) and "error" in exc.detail else {"error": {"code": "HTTP_ERROR", "message": str(exc.detail), "details": {}}}
    return JSONResponse(status_code=exc.status_code, content=detail)


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


def _parse_datetime(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.combine(datetime(1970, 1, 1).date(), time.fromisoformat(value))
        except ValueError:
            return None


def _summary(trace: Trace) -> TraceSummary:
    return TraceSummary(trace_id=trace.trace_id, schema_version=trace.schema_version, source_framework=trace.source_framework, scenario_id=trace.scenario_id, title=trace.title, status=trace.status, started_at=trace.started_at or "", duration_ms=trace.duration_ms, span_count=len(trace.spans), event_count=len(trace.events))


def _span_response(span: Span, trace_id: str) -> SpanResponse:
    return SpanResponse(trace_id=trace_id, span_id=span.span_id, parent_span_id=span.parent_span_id, kind=span.kind, name=span.name, status=span.status, duration_ms=span.duration_ms, detail=span.detail, error=span.error_code, started_at=span.started_at, ended_at=span.ended_at, attributes=span.attributes_json or {})


def _event_response(event: TraceEvent, trace_id: str) -> EventResponse:
    return EventResponse(trace_id=trace_id, event_id=event.event_id, sequence=event.sequence, span_id=event.span_id, event_type=event.event_type, label=event.label, occurred_at=event.occurred_at, at_ms=event.at_ms, payload=event.payload_json)


def _trace_response(trace: Trace) -> TraceResponse:
    spans = sorted(trace.spans, key=lambda item: item.id)
    events = sorted(trace.events, key=lambda item: item.sequence)
    return TraceResponse(**_summary(trace).model_dump(), summary=trace.summary, ended_at=trace.ended_at, spans=[_span_response(item, trace.trace_id) for item in spans], events=[_event_response(item, trace.trace_id) for item in events], metadata=trace.metadata_json or {})


@app.get("/api/v1/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectResponse]:
    projects = db.scalars(select(Project).order_by(Project.created_at)).all()
    return [ProjectResponse(project_id=item.id, name=item.name, slug=item.slug, trace_count=len(item.traces)) for item in projects]


@app.get("/api/v1/traces", response_model=PaginatedTraces)
def list_traces(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    scenario_id: str | None = Query(None, alias="scenario"),
    q: str | None = Query(None, max_length=128),
    db: Session = Depends(get_db),
) -> PaginatedTraces:
    query = select(Trace).order_by(Trace.created_at.desc())
    count_query = select(func.count()).select_from(Trace)
    if status_filter:
        query = query.where(Trace.status == status_filter)
        count_query = count_query.where(Trace.status == status_filter)
    if scenario_id:
        query = query.where(Trace.scenario_id == scenario_id)
        count_query = count_query.where(Trace.scenario_id == scenario_id)
    if q:
        query = query.where(Trace.title.ilike(f"%{q}%"))
        count_query = count_query.where(Trace.title.ilike(f"%{q}%"))
    total = db.scalar(count_query) or 0
    traces = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return PaginatedTraces(items=[_summary(trace) for trace in traces], total=total, page=page, page_size=page_size)


def _get_trace(trace_id: str, db: Session) -> Trace:
    trace = db.scalar(select(Trace).where(Trace.trace_id == trace_id))
    if trace is None:
        raise _error("NOT_FOUND", "trace not found", {"trace_id": trace_id}, 404)
    return trace


@app.get("/api/v1/traces/{trace_id}", response_model=TraceResponse)
def get_trace(trace_id: str, db: Session = Depends(get_db)) -> TraceResponse:
    return _trace_response(_get_trace(trace_id, db))


@app.get("/api/v1/traces/{trace_id}/spans", response_model=list[SpanResponse])
def get_spans(trace_id: str, db: Session = Depends(get_db)) -> list[SpanResponse]:
    trace = _get_trace(trace_id, db)
    return [_span_response(item, trace.trace_id) for item in sorted(trace.spans, key=lambda span: span.id)]


@app.get("/api/v1/traces/{trace_id}/events", response_model=list[EventResponse])
def get_events(trace_id: str, db: Session = Depends(get_db)) -> list[EventResponse]:
    trace = _get_trace(trace_id, db)
    return [_event_response(item, trace.trace_id) for item in sorted(trace.events, key=lambda event: event.sequence)]


def _persist_trace(trace_input: TraceInput, db: Session) -> Trace:
    if db.scalar(select(Trace).where(Trace.trace_id == trace_input.trace_id)) is not None:
        raise _error("TRACE_EXISTS", "trace_id already exists", {"trace_id": trace_input.trace_id}, 409)
    trace = Trace(trace_id=trace_input.trace_id, schema_version=trace_input.schema_version, source_framework=trace_input.source_framework, scenario_id=trace_input.scenario_id, title=trace_input.title, summary=trace_input.summary, status=trace_input.status, started_at=_parse_datetime(trace_input.started_at), ended_at=_parse_datetime(trace_input.ended_at), duration_ms=trace_input.duration_ms, metadata_json=trace_input.metadata)
    trace.spans = [Span(trace_id=trace_input.trace_id, span_id=item.span_id, parent_span_id=item.parent_span_id, kind=item.kind, name=item.name, status=item.status, started_at=_parse_datetime(item.started_at), ended_at=_parse_datetime(item.ended_at), duration_ms=item.duration_ms, detail=item.detail, error_code=item.error, attributes_json=item.attributes) for item in trace_input.spans]
    trace.events = [TraceEvent(trace_id=trace_input.trace_id, event_id=item.event_id, span_id=item.span_id, sequence=item.sequence, event_type=item.event_type, label=item.label, occurred_at=_parse_datetime(item.occurred_at), at_ms=item.at_ms, payload_json=item.payload) for item in trace_input.events]
    db.add(trace)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _error("INVALID_TRACE", "trace could not be persisted", {"reason": "constraint violation"}, 422) from exc
    db.refresh(trace)
    return trace


@app.post("/api/v1/traces/import", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
async def import_trace(request: Request, db: Session = Depends(get_db)) -> TraceResponse:
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 1_048_576:
        raise TraceValidationError("trace payload exceeds 1 MiB", code="LIMIT_EXCEEDED")
    trace_input = parse_json_bytes(await request.body())
    return _trace_response(_persist_trace(trace_input, db))


@app.get("/api/v1/scenarios", response_model=list[ScenarioResponse])
def list_scenarios() -> list[ScenarioResponse]:
    return [ScenarioResponse(scenario_id=key, name=value["name"], description=value["description"], strategies=value["strategies"]) for key, value in SCENARIOS.items()]


def _experiment_response(experiment: Experiment) -> ExperimentResponse:
    result = experiment.result_json or {}
    return ExperimentResponse(experiment_id=experiment.id, scenario_id=experiment.scenario_id, strategy_id=experiment.strategy_id, trace_id=experiment.trace_id, status=experiment.status, retries=experiment.retries, virtual_duration_ms=experiment.virtual_duration_ms, assertion=(experiment.assertions_json or {}).get("assertion", ""), result=result.get("result", result), span_diff=result.get("span_diff", []), event_diff=result.get("event_diff", []))


@app.post("/api/v1/experiments", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)) -> ExperimentResponse:
    if payload.scenario_id not in SCENARIOS:
        raise _error("SCENARIO_NOT_FOUND", "scenario not found", {"scenario_id": payload.scenario_id}, 404)
    if not any(item["id"] == payload.strategy_id for item in SCENARIOS[payload.scenario_id]["strategies"]):
        raise _error("STRATEGY_NOT_FOUND", "strategy is not available for scenario", {"strategy_id": payload.strategy_id}, 422)
    if payload.trace_id:
        _get_trace(payload.trace_id, db)
    payload_bytes = json.dumps(payload.input, sort_keys=True, separators=(",", ":")).encode()
    experiment = Experiment(trace_id=payload.trace_id, scenario_id=payload.scenario_id, strategy_id=payload.strategy_id, input_hash=hashlib.sha256(payload_bytes).hexdigest(), input_json=payload.input)
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return _experiment_response(experiment)


@app.post("/api/v1/experiments/{experiment_id}/run", response_model=ExperimentResponse)
def run_experiment(experiment_id: str, db: Session = Depends(get_db)) -> ExperimentResponse:
    experiment = db.get(Experiment, experiment_id)
    if experiment is None:
        raise _error("NOT_FOUND", "experiment not found", {"experiment_id": experiment_id}, 404)
    result = run_mock(scenario_id=experiment.scenario_id, strategy_id=experiment.strategy_id, input_data=experiment.input_json or {})
    experiment.status = result["status"]
    experiment.retries = int(result.get("retries", 0))
    experiment.virtual_duration_ms = int(result.get("virtual_duration_ms", 0))
    experiment.result_json = result
    experiment.assertions_json = {"assertion": result.get("assertion", "")}
    experiment.evaluations.append(Evaluation(assertion=result.get("assertion", ""), passed=result["status"] == "completed", span_diff_json=result.get("span_diff", []), event_diff_json=result.get("event_diff", [])))
    db.commit()
    db.refresh(experiment)
    return _experiment_response(experiment)


@app.get("/api/v1/experiments/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)) -> ExperimentResponse:
    experiment = db.get(Experiment, experiment_id)
    if experiment is None:
        raise _error("NOT_FOUND", "experiment not found", {"experiment_id": experiment_id}, 404)
    return _experiment_response(experiment)
