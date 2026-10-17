# AgentScope 架构说明

## 1. 总体结构

采用单仓库、前后端分层：

```text
apps/web   React + TypeScript + Vite  ── TraceDataSource ── fixtures / API adapter
apps/api   FastAPI + Pydantic         ── application services ── repository/DB (P1)
packages/schema（可选共享契约）        ── 版本化 Trace/Span/Event 类型
```

静态 Demo 让 `apps/web` 使用本地合成 fixture 完成闭环；`TraceDataSource` 保持接口稳定，API adapter 可在不改页面业务契约的情况下接入 FastAPI。当前 API 已提供 SQLite/Alembic 持久化、受限导入和确定性实验端点；PostgreSQL 为自托管 profile。

## 2. 前端边界

- `features/explorer`：列表、筛选、统计。
- `features/trace-detail`：Graph、Inspector、Timeline、回放状态。
- `features/failure-lab`：策略选择、确定性模拟和对比。
- `lib/data-source`：fixture/API 数据源适配；不直接在组件内 fetch。
- `lib/validation`：Zod schema、大小/深度/数量限制、关系校验和安全字段拒绝。
- `types`：显式 schema 版本和领域类型。

服务器状态（未来 API）与本地回放状态分开；回放以 `event_index` 为唯一推进指针，禁止以墙上时钟产生非确定结果。

## 3. 数据流

```text
fixture/API/导入文件
        ↓ validate + normalize
TraceDataSource.list/get
        ↓
Explorer → Trace Detail
        ↓ selectedTrace + eventIndex
Graph / Inspector / Timeline
        ↓
Failure Lab → deterministic MockResult → comparison view
```

导入内容只作为数据处理，不作为 HTML、脚本或命令执行。所有文本默认按纯文本渲染。

## 4. 领域模型

- `Trace`：一次记录，含 `trace_id`、`schema_version`、状态、起止时间、根 span 和 spans/events。
- `Span`：父子层级、类型、状态、时间、输入输出摘要和错误引用。
- `Event`：稳定序号、时间、span 引用、事件类型和脱敏 payload。
- `FailureScenario`：fixture 中声明的故障语义，不是任意代码。
- `MockResult`：策略 ID、确定性结果、断言、重试次数、虚拟耗时和 span diff。

## 5. 安全边界

- 仅接受 JSON 数据，不执行导入内容。
- 限制文件字节数、对象深度、数组/节点/事件数量和字符串长度。
- 校验 ID 唯一、父节点存在、无环、事件顺序连续、时间范围合理。
- 错误信息不回显令牌、环境变量或完整敏感 payload；日志只记录摘要。
- P0 不提供任意工具调用、shell、网络代理或真实 LLM 执行。

## 6. 部署形态

- 静态 Demo：Vite build 输出可部署到 GitHub Pages；路由使用可配置 base，必要时提供 404 fallback。
- 自托管 P1：API、Web、SQLite/Postgres；Docker Compose 仅在 Docker 可用时验证。
- 任何后端公网部署必须有认证、限流、脱敏、日志和独立授权；未满足时标记 `self-host-ready`，不称为 live。

## 7. 可观测性与失败语义

API 使用稳定错误码（如 `INVALID_TRACE`、`LIMIT_EXCEEDED`、`RELATION_INVALID`、`NOT_FOUND`）。前端区分加载、空数据、导入失败、数据损坏和未知错误，不能用空列表掩盖失败。
