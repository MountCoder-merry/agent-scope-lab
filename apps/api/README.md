# AgentScope API

P1 FastAPI 骨架。当前只提供无副作用的 health 和空 trace 列表契约；数据仓库、导入和 Mock Runner 将在 M6/M7 接入。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest
```
