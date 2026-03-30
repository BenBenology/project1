# Scripts 说明

## `start_demo.py`

用于本地一键启动整个 demo：

- 启动 FastAPI 后端
- 启动 Streamlit 前端
- 自动读取项目根目录下的 `.env`
- 按 `Ctrl + C` 时同时关闭两个进程

当前更适合用于本地联调：

- FastAPI 后端会连接 SQLite
- 后端会执行真实 source 与 mock fallback 的组合流程
- Streamlit 前端默认消费后端 API，而不是只看静态 demo

运行方式：

```bash
python3 scripts/start_demo.py
```

适合当前阶段快速验证产品流程，不需要分别记住两条启动命令。
