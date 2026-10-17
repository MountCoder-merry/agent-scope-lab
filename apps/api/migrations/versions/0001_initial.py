"""initial AgentScope persistence schema"""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("projects", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(128), nullable=False), sa.Column("slug", sa.String(128), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)
    op.create_table("traces", sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id"), nullable=True), sa.Column("trace_id", sa.String(128), nullable=False), sa.Column("schema_version", sa.String(32), nullable=False), sa.Column("source_framework", sa.String(64), nullable=False), sa.Column("scenario_id", sa.String(64), nullable=False), sa.Column("title", sa.String(256), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("ended_at", sa.DateTime(timezone=True)), sa.Column("duration_ms", sa.Integer(), nullable=False), sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("trace_id"))
    op.create_index("ix_traces_trace_id", "traces", ["trace_id"], unique=True)
    op.create_index("ix_traces_project_id", "traces", ["project_id"])
    op.create_index("ix_traces_status", "traces", ["status"])
    op.create_index("ix_traces_scenario_id", "traces", ["scenario_id"])
    op.create_index("ix_traces_status_scenario", "traces", ["status", "scenario_id"])
    op.create_table("spans", sa.Column("id", sa.String(36), primary_key=True), sa.Column("trace_id", sa.String(128), sa.ForeignKey("traces.trace_id", ondelete="CASCADE"), nullable=False), sa.Column("span_id", sa.String(128), nullable=False), sa.Column("parent_span_id", sa.String(128)), sa.Column("kind", sa.String(32), nullable=False), sa.Column("name", sa.String(256), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("ended_at", sa.DateTime(timezone=True)), sa.Column("duration_ms", sa.Integer(), nullable=False), sa.Column("detail", sa.Text(), nullable=False), sa.Column("error_code", sa.String(256)), sa.Column("attributes_json", sa.JSON(), nullable=False), sa.UniqueConstraint("trace_id", "span_id", name="uq_spans_trace_span"))
    op.create_index("ix_spans_trace_id", "spans", ["trace_id"])
    op.create_table("events", sa.Column("id", sa.String(36), primary_key=True), sa.Column("trace_id", sa.String(128), sa.ForeignKey("traces.trace_id", ondelete="CASCADE"), nullable=False), sa.Column("event_id", sa.String(128), nullable=False), sa.Column("span_id", sa.String(128), nullable=False), sa.Column("sequence", sa.Integer(), nullable=False), sa.Column("event_type", sa.String(128), nullable=False), sa.Column("label", sa.String(256), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True)), sa.Column("at_ms", sa.Integer(), nullable=False), sa.Column("payload_json", sa.JSON()), sa.UniqueConstraint("trace_id", "event_id", name="uq_events_trace_event"), sa.UniqueConstraint("trace_id", "sequence", name="uq_events_trace_sequence"))
    op.create_index("ix_events_trace_id", "events", ["trace_id"])
    op.create_table("experiments", sa.Column("id", sa.String(36), primary_key=True), sa.Column("trace_id", sa.String(128), sa.ForeignKey("traces.trace_id", ondelete="CASCADE")), sa.Column("scenario_id", sa.String(64), nullable=False), sa.Column("strategy_id", sa.String(64), nullable=False), sa.Column("input_hash", sa.String(64), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("result_json", sa.JSON(), nullable=False), sa.Column("assertions_json", sa.JSON(), nullable=False), sa.Column("retries", sa.Integer(), nullable=False), sa.Column("virtual_duration_ms", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_experiments_trace_id", "experiments", ["trace_id"])
    op.create_index("ix_experiments_scenario_id", "experiments", ["scenario_id"])
    op.create_index("ix_experiments_status", "experiments", ["status"])
    op.create_table("evaluations", sa.Column("id", sa.String(36), primary_key=True), sa.Column("experiment_id", sa.String(36), sa.ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False), sa.Column("assertion", sa.Text(), nullable=False), sa.Column("passed", sa.Boolean(), nullable=False), sa.Column("span_diff_json", sa.JSON(), nullable=False), sa.Column("event_diff_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_evaluations_experiment_id", "evaluations", ["experiment_id"])


def downgrade() -> None:
    op.drop_index("ix_evaluations_experiment_id", table_name="evaluations")
    op.drop_table("evaluations")
    op.drop_index("ix_experiments_status", table_name="experiments")
    op.drop_index("ix_experiments_scenario_id", table_name="experiments")
    op.drop_index("ix_experiments_trace_id", table_name="experiments")
    op.drop_table("experiments")
    op.drop_index("ix_events_trace_id", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_spans_trace_id", table_name="spans")
    op.drop_table("spans")
    op.drop_index("ix_traces_status_scenario", table_name="traces")
    op.drop_index("ix_traces_scenario_id", table_name="traces")
    op.drop_index("ix_traces_status", table_name="traces")
    op.drop_index("ix_traces_project_id", table_name="traces")
    op.drop_index("ix_traces_trace_id", table_name="traces")
    op.drop_table("traces")
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_table("projects")
