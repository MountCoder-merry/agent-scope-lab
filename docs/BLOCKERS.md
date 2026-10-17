# AgentScope 阻塞项

## 当前阻塞

### Python 依赖传递审计查询超时

- **状态**：待处理，不阻塞本地功能验证。
- **证据**：npm audit 已返回 0 vulnerabilities；`pip-audit` 对锁定的顶层运行依赖（`--disable-pip --no-deps`）返回 `No known vulnerabilities found`，但完整传递依赖解析在当前 PyPI/OSV 查询环境超时。
- **影响**：不能把受限顶层结果扩大为完整 Python 供应链审计结论。
- **安全处理**：不伪造审计结果；保留 lockfile、记录命令和阻塞原因。
- **解除方式**：在可访问 PyPI/OSV 的环境执行不带 `--no-deps` 的完整锁定依赖审计，并保存结果。

### Docker CLI 缺失

- **状态**：待处理，非当前 M0/M1 阻塞
- **证据**：`docker --version` 返回命令不存在。
- **影响**：无法在当前环境执行 Docker Compose、自托管后端容器和容器级集成验证。
- **安全处理**：不自动安装或修改系统级配置。
- **解除方式**：在本机安装并启用 Docker Desktop（由用户按其安全策略完成），然后重新运行容器门禁。
- **可继续工作**：React/FastAPI 源码、单元测试、静态构建、Playwright 浏览器验证和部署文档。

GitHub 发布阻塞已解除：已创建专用公开仓库 `MountCoder-merry/agent-scope-lab`，Pages workflow 和线上浏览器核验均通过。Docker 与 Python 依赖审计仍保持阻塞。
