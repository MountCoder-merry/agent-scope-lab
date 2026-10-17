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
