# AgentScope Autopilot Kit — 使用说明

此套件是**开发计划 + 自主执行规则 + 主控提示词 + Windows PowerShell 有界续跑工具**，并非已实现的 AgentScope 应用。

## 套件内容

- `AgentScope_全自主开发计划书.md`：产品、架构、里程碑、验收、自动化和部署门禁。
- `AGENTS.md`：Codex 的可持续工程规范和安全授权范围。
- `CODEX_MASTER_PROMPT.md`：在 Codex 中执行的长时自主任务指令。
- `RUN_AGENT_SCOPE.ps1`：单次启动、退出后续跑、日志、停止条件。
- `references/Codex开发流程规范.md`：你提供的原始软件生命周期规范。

## 开始实验（Windows）

1. 安装 Node.js、Python、Git、Codex CLI，建议安装 GitHub CLI。
2. 新建一个**空的专用项目目录**（如 `D:\ai-coding-projects\agent-scope-lab`），把套件文件完整复制到里面，尤其保留 `references/`。
3. 打开 PowerShell，进入该目录并阅读 `AGENTS.md` 和计划书中的授权边界。
4. 运行：

```powershell
git init -b main
codex --version
codex exec --help
gh auth status
# 如未登录 GitHub，用户自己一次性执行 gh auth login
.\RUN_AGENT_SCOPE.ps1 -MaxHours 6 -MaxTurns 12
```

如系统 PowerShell 策略禁止运行该脚本，应使用自己信任和审核过的签名/执行配置；**不要为了这个实验全局关闭安全策略**。

也可以不用续跑器，直接执行单次任务：

```powershell
Get-Content -Raw -Encoding UTF8 .\CODEX_MASTER_PROMPT.md | codex exec --approve-for-me --json -
```

## 查看状态

- `docs/AUTONOMOUS_STATE.json`：当前阶段与阻塞。
- `docs/WORKLOG.md`：Codex 具体做了什么、跑过什么测试。
- `docs/BLOCKERS.md`：需要外部授权的项目。
- `.codex-run/`：各轮 JSONL 日志（敏感，勿提交或公开）。

## 预期效果

Codex **尽力持续多个小时处理预授权的本地任务**，自动完成文档、代码、测试、修复、视觉迭代；授权和门禁满足时自动为本项目发布**不含敏感数据**的 GitHub Pages Demo。不保证 6 小时内全部完成，不保证 GitHub Pages 的启用、网络和配额无需人工介入。

## 中止

```powershell
# 运行器会在本轮 Codex 结束后读取 STOP；立即停止请使用 Ctrl+C
New-Item -ItemType File -Force .\.codex-run\STOP
```

**注意：** “不重复询问小任务”不等于“完全无限权限”。默认不启用 `--yolo`；不会主动购买服务或修改你其他仓库。
