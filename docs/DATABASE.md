# 数据库设计（P1 草案）

P0 不需要数据库，使用版本化只读 fixture。P1 使用 SQLAlchemy 2 + Alembic，默认 SQLite，保持 PostgreSQL 兼容。

## 表

### `traces`

`id`（内部 UUID）、`trace_id`（唯一文本）、`schema_version`、`scenario_id`、`status`、`started_at`、`ended_at`、`metadata_json`、`created_at`。

### `spans`

`id`、`trace_id`、`span_id`（trace 内唯一）、`parent_span_id`（可空）、`kind`、`name`、`status`、`started_at`、`ended_at`、`attributes_json`、`error_code`。

### `events`

`id`、`trace_id`、`event_id`（trace 内唯一）、`span_id`、`sequence`（trace 内唯一）、`event_type`、`occurred_at`、`payload_json`。

### `mock_runs`

`id`、`trace_id`、`scenario_id`、`strategy_id`、`input_hash`、`result_json`、`assertions_json`、`created_at`。

## 约束与索引

- `traces.trace_id` 唯一；`(trace_id, span_id)`、`(trace_id, event_id)`、`(trace_id, sequence)` 唯一。
- `spans.parent_span_id` 在同一 trace 内存在；删除 trace 级联其 spans/events/mock_runs。
- 为 `status`、`scenario_id`、`started_at`、`events(trace_id, sequence)` 建索引。
- JSON 字段只存已校验、已脱敏内容；不存 token、密码或未限制的大 payload。

## 迁移与恢复

- 每次 schema 改动必须有 Alembic migration 和向后兼容说明。
- 导入使用事务，任何关系校验失败全部回滚。
- SQLite 重启验证属于 M6；PostgreSQL 只做兼容集成测试，不在 P0 引入生产依赖。
