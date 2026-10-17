"""Persistent domain models for recorded traces and experiments."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def uuid_str() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(128))
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    traces: Mapped[list[Trace]] = relationship(back_populates="project")


class Trace(Base):
    __tablename__ = "traces"
    __table_args__ = (Index("ix_traces_status_scenario", "status", "scenario_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    trace_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    schema_version: Mapped[str] = mapped_column(String(32), default="1.0")
    source_framework: Mapped[str] = mapped_column(String(64), default="synthetic")
    scenario_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    project: Mapped[Project | None] = relationship(back_populates="traces")
    spans: Mapped[list[Span]] = relationship(back_populates="trace", cascade="all, delete-orphan")
    events: Mapped[list[TraceEvent]] = relationship(back_populates="trace", cascade="all, delete-orphan")
    experiments: Mapped[list[Experiment]] = relationship(back_populates="trace", cascade="all, delete-orphan")


class Span(Base):
    __tablename__ = "spans"
    __table_args__ = (UniqueConstraint("trace_id", "span_id", name="uq_spans_trace_span"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    trace_id: Mapped[str] = mapped_column(ForeignKey("traces.trace_id", ondelete="CASCADE"), index=True)
    span_id: Mapped[str] = mapped_column(String(128))
    parent_span_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    kind: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(16))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    detail: Mapped[str] = mapped_column(Text, default="")
    error_code: Mapped[str | None] = mapped_column(String(256), nullable=True)
    attributes_json: Mapped[dict] = mapped_column(JSON, default=dict)

    trace: Mapped[Trace] = relationship(back_populates="spans")


class TraceEvent(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("trace_id", "event_id", name="uq_events_trace_event"), UniqueConstraint("trace_id", "sequence", name="uq_events_trace_sequence"))

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    trace_id: Mapped[str] = mapped_column(ForeignKey("traces.trace_id", ondelete="CASCADE"), index=True)
    event_id: Mapped[str] = mapped_column(String(128))
    span_id: Mapped[str] = mapped_column(String(128))
    sequence: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(128))
    label: Mapped[str] = mapped_column(String(256), default="")
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    at_ms: Mapped[int] = mapped_column(Integer, default=0)
    payload_json: Mapped[object] = mapped_column(JSON, nullable=True)

    trace: Mapped[Trace] = relationship(back_populates="events")


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    trace_id: Mapped[str | None] = mapped_column(ForeignKey("traces.trace_id", ondelete="CASCADE"), nullable=True, index=True)
    scenario_id: Mapped[str] = mapped_column(String(64), index=True)
    strategy_id: Mapped[str] = mapped_column(String(64))
    input_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="created", index=True)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    assertions_json: Mapped[dict] = mapped_column(JSON, default=dict)
    retries: Mapped[int] = mapped_column(Integer, default=0)
    virtual_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    trace: Mapped[Trace | None] = relationship(back_populates="experiments")
    evaluations: Mapped[list[Evaluation]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), index=True)
    assertion: Mapped[str] = mapped_column(Text, default="")
    passed: Mapped[bool] = mapped_column(default=False)
    span_diff_json: Mapped[list] = mapped_column(JSON, default=list)
    event_diff_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    experiment: Mapped[Experiment] = relationship(back_populates="evaluations")
