"""Versioned HTTP contracts and bounded trace validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

TraceStatus = Literal["failed", "completed", "running"]
SpanStatus = Literal["ok", "error", "pending"]


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ok"]
    schema_version: int = 1


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class SpanInput(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    span_id: str = Field(validation_alias=AliasChoices("span_id", "spanId"), min_length=1, max_length=128)
    parent_span_id: str | None = Field(default=None, validation_alias=AliasChoices("parent_span_id", "parentSpanId"), max_length=128)
    kind: Literal["agent", "tool", "parser"]
    name: str = Field(min_length=1, max_length=256)
    status: SpanStatus
    duration_ms: int = Field(default=0, validation_alias=AliasChoices("duration_ms", "durationMs"), ge=0, le=86_400_000)
    detail: str = Field(default="", max_length=16_384)
    error: str | None = Field(default=None, max_length=256)
    started_at: datetime | None = Field(default=None, validation_alias=AliasChoices("started_at", "startedAt"))
    ended_at: datetime | None = Field(default=None, validation_alias=AliasChoices("ended_at", "endedAt"))
    attributes: dict[str, Any] = Field(default_factory=dict)


class EventInput(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    event_id: str = Field(validation_alias=AliasChoices("event_id", "eventId"), min_length=1, max_length=128)
    sequence: int = Field(ge=0, le=5000)
    span_id: str = Field(validation_alias=AliasChoices("span_id", "spanId"), min_length=1, max_length=128)
    event_type: str = Field(default="span.started", validation_alias=AliasChoices("event_type", "eventType", "type"), min_length=1, max_length=128)
    label: str = Field(default="", max_length=256)
    occurred_at: datetime | None = Field(default=None, validation_alias=AliasChoices("occurred_at", "occurredAt"))
    at_ms: int = Field(default=0, validation_alias=AliasChoices("at_ms", "atMs"), ge=0, le=86_400_000)
    payload: Any = None


class TraceInput(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    trace_id: str = Field(validation_alias=AliasChoices("trace_id", "traceId"), min_length=1, max_length=128)
    schema_version: str = Field(default="1.0", validation_alias=AliasChoices("schema_version", "schemaVersion"), max_length=32)
    source_framework: str = Field(default="synthetic", validation_alias=AliasChoices("source_framework", "sourceFramework"), max_length=64)
    scenario_id: str = Field(default="unknown", validation_alias=AliasChoices("scenario_id", "scenarioId", "scenario"), max_length=64)
    title: str = Field(default="", max_length=256)
    summary: str = Field(default="", max_length=16_384)
    status: TraceStatus
    started_at: datetime | str = Field(validation_alias=AliasChoices("started_at", "startedAt"))
    ended_at: datetime | str | None = Field(default=None, validation_alias=AliasChoices("ended_at", "endedAt"))
    duration_ms: int = Field(default=0, validation_alias=AliasChoices("duration_ms", "durationMs"), ge=0, le=86_400_000)
    spans: list[SpanInput] = Field(min_length=1, max_length=500)
    events: list[EventInput] = Field(min_length=1, max_length=5000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("started_at", "ended_at", mode="before")
    @classmethod
    def normalize_time(cls, value: Any) -> Any:
        return value


class TraceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: str
    schema_version: str
    source_framework: str
    scenario_id: str
    title: str
    status: TraceStatus
    started_at: datetime | str
    duration_ms: int = Field(ge=0)
    span_count: int = Field(ge=0)
    event_count: int = Field(ge=0)


class SpanResponse(SpanInput):
    trace_id: str


class EventResponse(EventInput):
    trace_id: str


class TraceResponse(TraceSummary):
    summary: str
    ended_at: datetime | str | None = None
    spans: list[SpanResponse]
    events: list[EventResponse]
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaginatedTraces(BaseModel):
    schema_version: int = 1
    items: list[TraceSummary]
    total: int
    page: int
    page_size: int


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    slug: str
    trace_count: int = 0


class ScenarioResponse(BaseModel):
    scenario_id: str
    name: str
    description: str
    strategies: list[dict[str, str]]


class ExperimentCreate(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    scenario_id: str = Field(validation_alias=AliasChoices("scenario_id", "scenarioId"), min_length=1, max_length=64)
    strategy_id: str = Field(validation_alias=AliasChoices("strategy_id", "strategyId"), min_length=1, max_length=64)
    trace_id: str | None = Field(default=None, validation_alias=AliasChoices("trace_id", "traceId"), max_length=128)
    input: dict[str, Any] = Field(default_factory=dict)


class ExperimentResponse(BaseModel):
    experiment_id: str
    schema_version: int = 1
    scenario_id: str
    strategy_id: str
    trace_id: str | None
    status: Literal["created", "running", "completed", "failed"]
    retries: int = 0
    virtual_duration_ms: int = 0
    assertion: str = ""
    result: dict[str, Any] = Field(default_factory=dict)
    span_diff: list[dict[str, Any]] = Field(default_factory=list)
    event_diff: list[dict[str, Any]] = Field(default_factory=list)
