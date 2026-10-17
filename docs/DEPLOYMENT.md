# 部署与回滚

## 静态 Demo（P0）

1. 安装锁定依赖并运行 lint、typecheck、unit、build、E2E。
2. 使用 Vite 的生产构建产物部署到专用 GitHub Pages 仓库/分支。
3. 配置正确的 `base`，验证深链接、刷新、静态资源和 404 fallback。
4. 从独立浏览器执行核心旅程并记录 HTTP 状态；只有实际验证的 HTTPS URL 才写入状态文件。

静态 Demo 不含 API Key、账号、真实 trace 或服务端执行能力。

API 写请求默认使用 60 秒滑动窗口限流（每客户端 30 次，可通过 `AGENTSCOPE_WRITE_RATE_LIMIT` 配置），并输出不含请求体、查询参数或 Token 的结构化访问日志。多 worker/多副本环境仍需反向代理提供共享限流、认证和 TLS。

## 自托管（P1）

Docker Compose 目标服务为 `web`、`api` 和可选 `db`。当前环境 Docker 缺失，配置完成后需在 Docker 可用环境运行迁移、健康检查、API 集成和重启持久化验证。

## 回滚

- 静态 Demo：回滚到上一份已验证 Pages artifact/commit；不修改用户数据。
- API/DB：先停止写入，再按 migration 兼容策略回滚应用；数据库恢复独立于代码回滚。
- 发布记录包含版本、commit SHA、CI run、验证 URL 和已知限制。

## 发布门禁

- 高危安全问题为 0；依赖、构建和浏览器核心旅程通过。
- 未实际部署/验证时状态保持 `in_progress` 或 `blocked`，不得写入伪造 URL。
