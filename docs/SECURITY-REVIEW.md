# AgentScope 安全审查（M5/M8 基线）

更新时间：2026-10-17  
审查范围：`apps/web`、`apps/api`、导入边界、CI、Docker Compose、发布产物。

## 结论摘要

当前公开 Demo 的设计边界是“合成数据 + 浏览器内确定性 Mock”。未授权真实模型调用、任意工具执行、shell、网络代理、账号和密钥接入。安全门禁在依赖和运行环境可用时必须执行；没有实际执行的检查保持 `pending`，不视为通过。

| 项目 | 状态 | 证据/后续动作 |
| --- | --- | --- |
| 导入 JSON 不执行 | `reviewed` | Web 使用 JSON.parse + Zod；不得使用 `eval`/危险 HTML。新增 schema 时补充回归测试。 |
| Payload 大小/深度/数量限制 | `reviewed` | Web/API 导入限制 1 MiB；API 限制最大深度 12、500 spans、5000 events、16 KiB 字符串，并有回归测试。 |
| XSS/HTML 注入 | `reviewed` | UI 文本使用 React 默认转义；禁止 `dangerouslySetInnerHTML`。 |
| API secret/日志脱敏 | `reviewed` | 错误响应只返回稳定错误码和结构化 details；访问日志只记录 request id、方法、路径、状态、耗时和客户端标识，不记录 body/query/token；仓库扫描未发现真实令牌或 `.env`。公网 API 仍不发布。 |
| 写入限流 | `reviewed` | `RequestGuardMiddleware` 对 API 写请求使用 60 秒滑动窗口（默认 30 次/IP，可由 `AGENTSCOPE_WRITE_RATE_LIMIT` 调整），超限返回 `RATE_LIMITED`；多 worker 部署仍需在反向代理启用共享限流。 |
| 依赖审计 | `partial` | npm audit → 0 vulnerabilities；受限的 Python 顶层依赖审计（pinned requirements + `--no-deps`）→ no known vulnerabilities；完整传递依赖查询在当前 PyPI/OSV 环境超时，不能扩大声明。 |
| Git secret scan | `reviewed` | 工作树扫描仅发现 `.env.example` 占位密码和文档术语；无真实凭据。提交前继续复核。 |
| Docker 镜像/Compose | `static-reviewed` | 已加入非 root API 用户、健康检查和可选 Postgres；Docker CLI 缺失时不能声称容器通过。 |
| GitHub Pages | `reviewed` | 仅发布静态 `apps/web/dist`；新仓库 Actions 成功、HTTPS 200、资源 200 和独立浏览器 smoke 已有发布记录。 |

## 必须保持的约束

1. Trace、Span、Event 输入只被当作结构化数据渲染，不能作为 HTML、JavaScript、命令或 URL 代理指令执行。
2. 公开 Demo 不读取真实密钥，不调用付费 LLM，不向外部服务发送导入内容。
3. API 写操作必须有 payload 限制、严格 schema、事务和稳定错误码；错误消息不得回显 token、环境变量或完整敏感输入。
4. Docker 默认只暴露本地端口；将 API 暴露到公网前，必须增加认证、CORS allowlist、限流、超时、审计日志和 TLS。
5. `.env`、数据库卷和测试产物不得提交。 `.env.example` 只能包含占位符。

## 发布前操作清单

```powershell
npm run lint
npm run typecheck
npm run test:unit
npm run build
npm audit --omit=dev
python -m pytest -q apps/api
```

在 Python 审计工具可用时：

```powershell
python -m pip install pip-audit
pip-audit
```

仓库没有 requirements.txt 时，应改用已安装的 apps/api editable 环境或导出锁定依赖后审计，不要伪造命令结果。

## 风险分级

- **高危**：任意代码/命令执行、真实 secret 泄漏、未授权公网模型/工具调用。出现时停止发布。
- **中危**：导入绕过大小/关系校验、未脱敏日志、公开 API 无认证或无限制写入。修复或明确阻塞。
- **低危**：安全 header、缓存策略、文档或依赖更新遗漏。发布前修复或记录接受理由。

本审查文档不是渗透测试报告；它记录设计边界、可复现检查和当前环境限制。
