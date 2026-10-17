# 测试计划

## 单元测试

- Zod/Pydantic schema：合法 trace、缺字段、超限、未知字段和危险文本。
- 关系校验：重复 ID、缺父节点、循环、事件序号跳跃、时间倒置。
- 回放 reducer：每个 event index 的状态和重复播放结果稳定。
- Mock 策略：工具超时的两种策略输出、断言和 diff 稳定。

## 集成测试

- `TraceDataSource` fixture 读取和 API adapter 契约一致。
- FastAPI health/list/detail/import（M6）；导入失败不产生部分数据。
- SQLite migration、重启后数据保留（M6）。

## E2E / 浏览器验收

1. 首屏看到三个案例并能筛选工具超时。
2. 打开 Trace Detail，选择节点，时间轴推进后图和 Inspector 同步。
3. Failure Lab 分别运行基线和两种策略，看到稳定差异。
4. 导入合法 JSON 成功，非法 JSON 显示错误且页面保持可用。
5. 桌面和窄视口无横向滚动；键盘可到达主要控件。

## 工程门禁

按实际脚本运行 `npm run lint`、`npm run typecheck`、`npm run test:unit`、`npm run build`，以及可用时的 Playwright E2E。Python 服务运行 `ruff`/`mypy`/`pytest`（最终脚本名以 M2 工程初始化为准）。每次记录命令和退出码，不把未执行写成通过。

## 安全回归

- 导入数据永不进入 `innerHTML` 或命令执行路径。
- 限制文件大小、深度、数量和字符串长度。
- 检查构建产物和 Git 差异中没有密钥、`.env`、运行日志或用户资料。
