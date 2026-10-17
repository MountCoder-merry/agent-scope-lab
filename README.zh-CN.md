# AgentScope Lab

AgentScope 是一个本地优先的 AI Agent Trace 调试工作台。它用合成、脱敏的执行记录展示 Trace、Span 和事件，支持时间线回放、故障定位以及确定性 Mock 恢复策略对比。

> 当前公开 Demo 只运行浏览器内的静态 fixture 和 Mock，不需要 API Key，不会调用真实模型、网络工具或用户机器上的命令。

## 功能范围

- Trace Explorer：浏览三套合成案例、搜索状态和统计信息。
- Execution Graph：从已验证的 Span 父子关系渲染执行图。
- Span Inspector：查看状态、持续时间、错误类型和脱敏摘要。
- Event Replay：按稳定的事件序号回放记录，不重新执行 Agent。
- Failure Lab：比较有界重试、降级等确定性策略，结果可重复。
- JSON 导入：限制文件大小、数量、深度和关系；失败时不影响现有记录。
- FastAPI 自托管后端：SQLAlchemy/Alembic 持久化、受限 Trace 导入、查询、场景和确定性实验 API。

## 本地开发

需要 Node.js 22+；API 开发还需要 Python 3.11+。

```powershell
npm ci
npm run dev:web
```

可选 API：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".\apps\api[dev]"
python -m uvicorn apps.api.app.main:app --reload
```

## 验证命令

```powershell
npm run lint
npm run typecheck
npm run test:unit
npm run build
python -m pytest -q apps/api
```

浏览器 smoke 需要 Playwright Chromium：

```powershell
pip install playwright
python -m playwright install chromium
python C:\Users\Lenovo1\.agents\skills\webapp-testing\scripts\with_server.py `
  --server 'npm run dev:web -- --host 127.0.0.1' --port 5173 `
  -- python scripts/verify_ui.py
```

## Docker 自托管

Docker 当前环境若不可用，只能静态检查 Compose 文件；不要将未执行的容器检查写成通过。Docker 可用时：

```powershell
Copy-Item .env.example .env
docker compose up --build
```

打开 http://localhost:8080；API 健康检查为 http://localhost:8000/api/v1/health。

可选 PostgreSQL profile（后端是否使用 PostgreSQL 取决于 API 版本和 `DATABASE_URL` 配置）：

```powershell
docker compose --profile postgres up --build
```

默认数据卷为 `agentscope-api-data`。生产环境必须替换示例密码、使用受管控的 secrets，并在暴露网络前增加认证、限流、日志脱敏和 TLS。

## GitHub Pages 静态 Demo

`.github/workflows/pages.yml` 使用 GitHub Actions 构建 `apps/web/dist` 并部署到 Pages。仓库设置中需将 Pages 发布源设为 **GitHub Actions**。只有实际 HTTP 和浏览器验证通过后，才可把 URL 记录为已验证 Demo；没有验证时保持 `in_progress` 或 `blocked`。

## 安全边界与已知限制

- 导入 JSON 仅作为数据解析，禁止 HTML、脚本、shell、任意工具和网络副作用。
- 所有案例均为 synthetic fixtures；Recorded replay 不会重新调用模型或工具。
- API 已支持 SQLite 默认持久化、Alembic 初始迁移和 Mock 实验；PostgreSQL 使用 Compose profile，公网鉴权和真实 Agent 执行仍不在本 Demo 范围内。
- Docker、GitHub 权限或 Pages 设置不可用时，发布门禁会如实记录阻塞，不绕过安全控制。

详细审查见 [docs/SECURITY-REVIEW.md](docs/SECURITY-REVIEW.md)，部署和回滚见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

## English

See [README.md](README.md) for the bilingual project overview. AgentScope is a synthetic, side-effect-free trace workbench intended for local development and a public static demo.
