# AgentScope Lab

AgentScope 是一个本地优先的 AI Agent trace 调试工作台 Demo：查看合成执行记录、逐事件回放、定位 Span 级故障，并在无 API Key、无外部副作用的确定性 Mock 实验中比较恢复策略。

AgentScope is a local-first AI-agent trace debugging workbench. It visualizes synthetic execution records, replays recorded events, inspects span-level failures, and compares deterministic recovery experiments without API keys or external side effects.

## 当前状态

- 已完成 M0–M3：产品/架构契约、React/Vite Web、FastAPI health 骨架、三个合成案例、执行图、时间线、Span Inspector、Failure Lab、JSON 导入验证。
- 当前进入 M4：补齐浏览器导入/响应式覆盖、CI 与静态 Demo 发布门禁。
- Docker 当前环境不可用，因此容器化验证延后；见 [`docs/BLOCKERS.md`](docs/BLOCKERS.md)。

## 本地运行

需要 Node.js 22+。在仓库根目录执行：

```powershell
npm install
npm run dev:web
```

然后打开 Vite 输出的本地地址。API 骨架（可选）：

```powershell
python -m uvicorn apps.api.app.main:app --reload
```

## 验证

```powershell
npm run lint
npm run typecheck
npm run test:unit
npm run build
python -m pytest -q apps/api
```

浏览器 smoke（需要 Playwright Chromium）：

```powershell
python C:\Users\Lenovo1\.agents\skills\webapp-testing\scripts\with_server.py `
  --server 'npm run dev:web -- --host 127.0.0.1' --port 5173 `
  -- python scripts/verify_ui.py
```

截图和工程状态分别见 [`docs/screenshots/m3-desktop.png`](docs/screenshots/m3-desktop.png) 与 [`docs/AUTONOMOUS_STATE.json`](docs/AUTONOMOUS_STATE.json)。

## 边界

当前页面只处理版本化、脱敏、合成数据。`Recorded replay` 不会重新调用模型或工具；`Deterministic mock` 不是生产恢复；不提供任意代码执行、账号、计费或真实密钥接入。
