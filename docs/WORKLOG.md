# AgentScope 工作日志

## 2026-10-17 — M0 环境与仓库预检

### 完成

- 阅读 `AGENTS.md`、`AgentScope_全自主开发计划书.md`、`CODEX_MASTER_PROMPT.md` 和 `references/Codex开发流程规范.md`。
- 确认仓库位于 `E:\agent-scope\AgentScope_Codex`，当前为仅含启动套件的 Git 仓库，尚无应用源码和历史提交。
- 创建 `docs/` 状态目录及 M0 状态文件。
- 记录本机工具版本和 Docker 缺失情况。

### 实际检查

- `node --version` → `v22.22.0`
- `npm --version` → `10.9.4`
- `python --version` → `Python 3.14.6`
- `git --version` → `git version 2.55.0.windows.3`
- `gh --version` → `2.102.0`
- `codex --version` → `codex-cli 0.149.1`
- `gh auth status` → 已登录（未记录令牌）
- `docker --version` → 命令不存在

### 风险与下一步

- Docker 不可用会阻塞后续容器化验证，但不阻塞前端静态 Demo 和文档工作。
- 下一步进入 M1：落盘 PRD、架构、API、数据库、测试计划、部署方案和路线图。

## 2026-10-17 — M1 文档与 M2/M3 垂直切片

### 完成

- 新增 `docs/PRD.md`、`ARCHITECTURE.md`、`API.md`、`DATABASE.md`、`TEST-PLAN.md`、`DEPLOYMENT.md` 和 `decisions/ADR-0001-static-demo-first.md`。
- 创建 React + strict TypeScript + Vite Web 骨架和 FastAPI/Pydantic API health 骨架。
- 实现三个合成 trace 的 Explorer、数据驱动执行图、Span Inspector、事件时间轴和确定性 Failure Lab Mock。
- 使用 Playwright 在桌面视口验证案例切换、非法 JSON 错误节点、事件滑块和 Mock 运行，并保存 `docs/screenshots/m3-desktop.png`。

### 实际检查

- `npm install` → 通过。
- `npm run typecheck` → 通过（修复遗漏的 `@types/node` 和 Vitest 配置类型）。
- `npm run lint` → 通过。
- `npm run test:unit` → 2 tests passed。
- `npm run build` → Vite production build 通过。
- `python -m pytest -q apps/api` → 1 passed；有 FastAPI/Starlette 关于 httpx 的弃用警告。
- `python .../with_server.py --server 'npm run dev:web -- --host 127.0.0.1' ...` → Playwright UI smoke 通过。

### 已知问题与下一步

- 首次 UI smoke 暴露了根目录 dev 命令和测试选择器问题，已分别修正并重跑通过。
- 当前仍未实现 JSON 导入、Zod schema/关系验证、CI 和 Docker 验证；下一步补齐 M3 数据契约与导入错误路径。

### M3 收尾补充

- 新增 `src/validation.ts`：1 MiB 文件限制由 UI 执行，Zod 结构校验和 span/event 关系校验拒绝重复 ID、缺父节点、循环、未知 span 和非连续事件。
- Explorer 新增本地 JSON 导入入口；导入内容只作为数据，不执行文本/命令；重复 traceId 和无效 JSON 有可见状态提示。
- 新增关系错误回归单测；Web typecheck、lint、3 个 unit tests、build 和 Playwright smoke 均通过。
- Vite 构建出现 Zod 第三方包注释位置 warning，但不影响构建退出码（0）；后续可在依赖升级时复查。

### 初始化交付检查

- 新增项目级双语 `README.md`，说明本地启动、测试、截图和 P0 安全边界。
- 最终 JSON 状态解析和 `git diff --check` 通过；未创建提交、远程仓库或部署资源。

## 2026-10-17 — M4–M7 静态 Demo、API 闭环与实验引擎

### 完成

- Web 增加 HashRouter 路由、React Flow 图、TraceDataSource 契约、导入/空态/错误态/移动端处理和 Playwright smoke。
- API 增加 SQLAlchemy 模型、Alembic 初始迁移、SQLite 默认与 PostgreSQL URL 兼容、事务导入、分页筛选、实验生命周期和确定性 LangGraph/Mock Runner。
- CI、GitHub Pages workflow、Compose、自托管 Dockerfile、双语 README、安全审查和发布报告落盘。

### 实际检查

- `npm run lint` → 通过（0）。
- `npm run typecheck` → 通过（0）。
- `npm run test:unit` → 3 passed（0）。
- `npm run build` → 通过（0；Vite 第三方注释/chunk 大小 warning）。
- `python -m pytest -q apps/api` → 6 passed（0；LangGraph 弃用 warning）。
- `ruff check apps/api` → 通过（0）。
- 新 SQLite 执行 `alembic upgrade head` → 通过（0）。
- Playwright `scripts/verify_ui.py` → `ui-smoke: ok; routes/import/mobile verified`。
- Compose YAML 静态解析 → 通过；Docker CLI 缺失，未执行容器门禁。
- `npm audit` → 当前镜像 audit endpoint 404；`pip-audit` → 命令不可用，均记录为阻塞。

### Git 记录

- `bd071a0 feat: deliver trace workbench MVP`
- `0a0e45a feat: add self-hosted trace API and experiments`
- `079320b ci: add release, security, and self-hosting gates`

## 2026-10-17 — M9 公开静态 Demo 验证

### 远程门禁与修复

- 首次 CI API job 失败：setuptools 自动发现 `app` 与 `migrations` 两个顶层包；新增 `apps/api/pyproject.toml` 的显式 build-system/package discovery，提交 `b1899ef`。
- 首次 Pages job 因仓库未启用 Actions 构建源失败；通过 GitHub Pages API 将仓库配置为 `build_type=workflow` 后重跑。
- CI 成功运行：`39035418868`（Web、API、Browser smoke 全部通过）。
- Pages 成功运行：`39035418565`（build、configure-pages、upload、deploy 全部通过）。

### 线上证据

- `https://mountcoder-merry.github.io/agent-scope-lab/` → HTTP 200。
- 页面引用的 JS/CSS → HTTP 200，无资源 404。
- `AGENTSCOPE_BASE_URL=https://mountcoder-merry.github.io/agent-scope-lab/ python scripts/verify_ui.py` → `ui-smoke: ok; routes/import/mobile verified`。

### 未完成门禁

- Docker CLI 缺失，未伪造 Compose 构建/健康/重启通过。
- npm audit 已通过（0 vulnerabilities）；受限 pinned 顶层 Python 依赖审计返回 no known vulnerabilities；完整传递依赖查询超时，保持 pending。

## 2026-10-17 — M8 安全边界补强

- 新增 `apps/api/app/security.py`：1 MiB 请求头边界、API 写请求滑动窗口限流、`RATE_LIMITED`/`LIMIT_EXCEEDED` 稳定错误和不含 body/query/token 的 JSON 访问日志。
- 新增 `apps/api/tests/test_security.py`，覆盖限流窗口、超大请求拒绝、request id 和结构化日志证据。
- `python -m pytest -q apps/api` → 10 passed；`ruff check apps/api` → 通过。
- Docker CLI 和完整 Python 传递依赖漏洞查询仍是环境阻塞，未声明 M8 完整门禁通过。
- 受限审计发现的 `langgraph 0.6.11 / PYSEC-2026-83` 已通过将约束升级到 `langgraph>=1.0.10,<2` 修复；升级后的 runner/API 回归测试通过。
- 新增 0002 migration，覆盖已有 0001 schema 为 Experiment 增加 `input_json`；API run 现在会使用持久化的实验输入，不再只保存 hash。
