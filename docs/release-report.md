# AgentScope 发布报告

状态：`in_progress`  
版本：`0.1.0`  
日期：2026-10-17

## 交付范围

- Web：合成 Trace Explorer、Execution Graph、Span Inspector、事件回放、Failure Lab、JSON 导入。
- API：FastAPI + SQLAlchemy/Alembic、SQLite 默认持久化、受限导入、Trace 查询、场景和确定性实验端点。
- 工程化：Web/API CI、Playwright smoke、GitHub Pages workflow、Docker Compose 与自托管文档。
- 安全边界：无 API Key、无真实 LLM、无任意代码执行、无外部工具副作用。

## 验证证据

| 检查 | 命令/证据 | 结果 |
| --- | --- | --- |
| Web lint | `npm run lint` | 通过（0） |
| Web typecheck | `npm run typecheck` | 通过（0） |
| Web unit | `npm run test:unit` | 3 passed（0） |
| Web build | `npm run build` | 通过（0；有第三方注释和 chunk size warning） |
| API tests | `python -m pytest -q apps/api` | 5 passed（0；LangGraph 弃用警告） |
| API lint | `ruff check apps/api` | 通过（0） |
| Fresh migration | `alembic upgrade head` on fresh SQLite | 通过（0） |
| Browser smoke | `python scripts/verify_ui.py` | 通过；routes/import/mobile verified |
| Dependency audit | `npm audit --omit=dev` / `pip-audit` | npm audit blocked by registry 404；pip-audit unavailable |
| Docker Compose | `docker compose config` / `up --build` | YAML 静态解析通过；Docker CLI 缺失，不能声称容器通过 |
| Pages | Actions run + HTTPS/browser smoke | 未创建/验证公开 URL，保持阻塞 |

## 发布地址

- `public_demo_url`: `null`（未实际发布）
- `verified_demo_url`: `null`（未通过独立 HTTP/浏览器验证）

不要将仓库名推断为已发布地址。GitHub Pages 需要新仓库、Actions 权限和 Pages 发布源设置。

## 回滚

- 静态 Demo：将 Pages 部署回上一份已验证 artifact 或 commit；不修改用户数据。
- API/Compose：停止服务后回退镜像/commit；数据库卷独立备份，不执行破坏性迁移。
- CI/Pages：恢复上一份 workflow 版本并重新运行门禁，失败时保持 `blocked`。

## 已知限制与下一步

1. API 已完成 SQLAlchemy/Alembic、导入事务和确定性实验；PostgreSQL 与容器重启验证待 Docker/数据库环境。
2. 当前环境没有 Docker CLI，容器构建、健康检查和 Postgres profile 只能在 Docker 可用环境验证。
3. 公开仓库和 Pages URL 尚未在本任务中创建或验证；不得声称公网 Demo 已上线。
4. 创建新仓库并完成 Pages Actions/HTTPS 验证后，回填 commit SHA、CI run 链接和 Demo URL；在此之前保持 `in_progress`。
