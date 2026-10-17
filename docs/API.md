# API 契约（P1 草案）

P0 静态 Demo 通过同一 `TraceDataSource` 接口读取 fixtures；以下 HTTP 契约先固定领域边界，实际实现进入 M6。

## 版本与格式

- Base path：`/api/v1`
- Content-Type：`application/json`
- 响应必须包含 `schema_version` 或明确的 API version。
- 错误格式：`{"error":{"code":"INVALID_TRACE","message":"...","details":{}}}`

## 端点

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/health` | 进程健康检查，不访问外部工具 |
| GET | `/traces` | 分页、状态、场景和文本筛选 |
| GET | `/traces/{trace_id}` | 获取完整 trace/span/event |
| POST | `/traces/import` | 校验并导入受限 JSON；不执行 payload |
| GET | `/scenarios` | 列出可用 Mock 场景和策略元数据 |
| POST | `/scenarios/{scenario_id}/runs` | 运行确定性 Mock，返回结果和断言 |

## 导入约束

- 默认最大 body 1 MiB；最大深度 12；最多 500 spans、5000 events、每字段 16 KiB。
- `trace_id`、`span_id`、`event_id` 必须稳定且唯一；父引用必须存在且无环。
- 拒绝脚本标签、命令字段、未声明的可执行类型和超出 schema 的关系。
- 导入失败使用 4xx 稳定错误码，不部分写入。

## 未来实现要求

- 所有写操作使用事务；导入幂等键由客户端提供或由内容 hash 生成。
- 不把原始输入/输出直接写入普通日志；错误响应提供定位所需的字段路径而非秘密内容。
- 分页结果声明 `total` 是否精确；没有采集的统计返回 `null` 和 `availability: "not_collected"`。
