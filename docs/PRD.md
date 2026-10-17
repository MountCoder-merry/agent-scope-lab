# AgentScope 产品需求文档

## 1. 定位

AgentScope 是一个本地优先、公开 Demo 友好的 AI Agent trace 调试工作台：可视化记录的执行链路，定位失败原因，按原始事件回放，并在隔离的确定性 Mock 实验中比较恢复策略。

英文定位：An open-source debugging workbench for visualizing agent traces, replaying recorded events, and comparing controlled failure-recovery experiments.

## 2. 目标用户与价值

- 学习或开发 LangGraph/LangChain/自定义 Agent 的开发者。
- 需要复现工具调用、超时、非法输出等故障的工程师。
- 通过 GitHub 作品集快速判断项目工程质量的访客。

价值闭环：用户无需注册、API Key 或真实外部工具，就能从 trace 证据定位故障，逐事件回放，并比较两种预设恢复策略的结果。

## 3. 核心旅程

1. 打开静态 Demo，浏览三个合成案例：证据冲突、工具超时、非法 JSON。
2. 选择“工具超时”，查看 Trace Detail、执行图和 Span Inspector。
3. 移动时间轴，观察当前事件、节点状态和详情同步变化。
4. 进入 Failure Lab，选择一个恢复策略进行确定性 Mock 模拟。
5. 查看基线与策略结果的重试次数、耗时、断言和 Span 差异。
6. 可选导入 JSON；大小、结构、关系或危险字段不符合要求时显示可理解的错误。

## 4. P0 发布范围

- 统一 Trace/Span/Event schema，带 `schema_version`、稳定 ID、显式状态和时间顺序。
- 三套脱敏合成 fixture，页面展示不依赖网络或密钥。
- Trace Explorer：搜索、案例筛选、状态、耗时和故障标记。
- Trace Detail：基于数据的执行图、节点选择、Span Inspector、事件时间线。
- 稳定回放：同一输入多次按事件索引得到相同状态，不触发真实工具副作用。
- Failure Lab：工具超时至少提供两种预设恢复策略，输出可比较结果。
- JSON 导入：客户端限制体积、深度、节点数和关系；拒绝危险/循环/孤立/缺父节点数据。
- 统计：从当前 fixture 集合计算运行次数和故障率；无数据时明确显示“未采集”。
- 深色、桌面优先、移动可读、无横向溢出；关键交互可用键盘完成。
- 严格 TypeScript、单测、E2E、CI、构建、双语 README、架构和部署文档。

## 5. P1（P0 稳定后）

- FastAPI + Pydantic 查询和导入 API。
- SQLAlchemy 2 + Alembic，SQLite 本地和 PostgreSQL 兼容测试。
- 一个不含敏感数据的 LangGraph adapter 示例。
- 确定性 Mock Runner、实验断言、Span 级差异。
- Docker Compose 自托管前后端和 API/DB 集成测试。

## 6. 非目标

不做账号、计费、多租户、任意代码执行、真实用户 LLM 密钥、生产自动修复、跨云资源操作、大规模队列、完整 OTLP 兼容或非确定性完整重执行。

## 7. 关键术语与真实性约束

| 模式 | 说明 | UI 标签要求 |
|---|---|---|
| Recorded replay | 重放已保存 Event，不再次调用模型或工具 | `Recorded replay` |
| Mock experiment | 使用固定 fixture 和策略函数进行隔离模拟 | `Deterministic mock` |
| Real resumption | 未来 P1/P2 的受控后端能力，当前不提供 | 不得在 P0 中暗示已支持 |

任何演示数字都必须来自当前加载的数据；没有采集来源时显示“未采集”，不得伪造运行指标。

## 8. 验收标准

- 首屏在无网络、无密钥情况下可以打开并看到三案例。
- 选择案例后，图节点、事件时间轴和 Inspector 内容随事件索引一致变化。
- 同一案例同一策略连续运行两次，结果 JSON 稳定一致。
- 导入合法 fixture 成功；超过大小、缺父节点、循环关系或含危险字段的 JSON 被拒绝并说明原因。
- Failure Lab 至少展示基线与两种策略的可比较差异。
- `lint`、`typecheck`、单测、E2E（可运行环境）和 `build` 结果真实记录。
- GitHub Pages 静态构建不依赖服务端路由回退；若未实际发布，不填写伪造 URL。
