# AgentScope 路线图

状态只反映已验证交付，不把计划当成功能。

## M0 — 预检（已完成）

- [x] 阅读项目规则、计划书和原始流程规范。
- [x] 检查仓库、Git、Node.js、Python、Codex、GitHub CLI、Playwright、Docker。
- [x] 创建 `docs/AUTONOMOUS_STATE.json`、`WORKLOG.md`、`BLOCKERS.md`、`ENVIRONMENT.md`。

## M1 — 产品与设计文档（已完成）

- [x] `PRD.md`：用户、旅程、P0/P1 范围、非目标和验收标准。
- [x] `ARCHITECTURE.md`：Web/API 边界、TraceDataSource、回放和安全边界。
- [x] `DATABASE.md`、`API.md`、`TEST-PLAN.md`、`DEPLOYMENT.md`。
- [x] 至少一份 ADR，记录静态 Demo 优先和 Monorepo 边界。
- [x] 形成 M2–M9 可执行任务和每阶段门禁。

## M2 — 工程初始化（已完成）

- [x] `apps/web`：React + strict TypeScript + Vite，基础样式和测试脚本。
- [x] `apps/api`：FastAPI + Pydantic 健康检查骨架。
- [x] 锁定依赖、环境示例、CI 基础工作流。

## M3 — 端到端垂直切片（已完成）

- [x] 三个合成 Trace 的数据驱动执行图、节点 Inspector、时间轴和错误态。
- [x] Web 单测、API health 单测和最小 Playwright smoke。
- [x] Zod schema 校验、JSON 导入和关系错误态。

## M4–M5 — 公开演示 MVP 与发布门禁（进行中）

- [x] 三个案例、事件回放、Failure Lab Mock、JSON 导入、统计和基础响应式样式。
- [x] Playwright 覆盖导入文件和窄视口；CI、Pages workflow 和安全审查材料。
- [x] 新仓库 Actions 成功、Pages HTTPS 200、资源无 404，并完成独立浏览器线上 smoke（Docker/Python 审计仍为独立阻塞）。

## M6–M8 — 后端闭环与工程质量（部分完成）

- [x] FastAPI + SQLite/Alembic 迁移、查询/导入闭环、LangGraph adapter 和确定性 Mock Runner。
- [x] API 合同、实验生命周期、迁移和重启后 SQLite 保留测试。
- [x] API 集成测试、脱敏、写入限流、结构化日志和审计材料。
- [ ] Docker Compose 镜像/健康/重启门禁；Docker 可用后执行。

## M9 — 发布与维护（进行中）

- [x] 发布报告、变更记录、回滚说明、维护手册和线上 Demo 证据。
- [ ] Docker Compose 容器门禁和完整 Python 传递依赖审计完成后，才能将整体状态标记为 completed。
