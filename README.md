# 自动财报与文章研究 MVP

这是一个用于快速验证产品方向的 MVP 项目。当前版本使用：

- `FastAPI` 作为后端 API
- `Streamlit` 作为快速验证前端
- `mock 数据` 模拟财报、公告、新闻、深度文章

项目目标不是直接给出买卖指令，而是帮助用户更快完成公开信息收集、归类和初步阅读。

## 当前已实现

- 支持输入公司名、股票代码、行业词、主题词
- 创建一个 mock 抓取任务
- 模拟异步任务执行过程
- 返回结构化文档结果
- 在前端展示报告、公告、新闻和文章

## 项目结构

```text
project1/
├── backend/
│   ├── __init__.py
│   └── app/
│       ├── api/                # 路由层
│       ├── core/               # 配置层
│       ├── models/             # 数据模型
│       ├── repositories/       # 存储层，当前为内存实现
│       ├── services/           # 业务逻辑层
│       └── main.py             # FastAPI 入口
├── frontend/
│   └── streamlit_app.py        # Streamlit 入口
├── architecture.md             # 架构说明
├── agent.md                    # 协作约定
├── skills.md                   # 项目能力说明
├── tasks.md                    # 当前任务列表
├── Untitled.md                 # 产品方案与 PRD 草稿
├── .env.example
├── README.md
└── requirements.txt
```

## 快速启动

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 准备环境变量

```bash
cp .env.example .env
```

### 4. 一键启动 Demo

```bash
python3 scripts/start_demo.py
```

或者直接：

```bash
bash scripts/run_demo.sh
```

启动后可直接访问：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8501`

按 `Ctrl + C` 会同时关闭后端和前端。

### 5. 如果你想分别启动

先启动后端：

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

后端地址：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

再启动前端：

另开一个终端运行：

```bash
streamlit run frontend/streamlit_app.py --server.port 8501
```

然后访问：

- `http://127.0.0.1:8501`

## 主流程

1. 在 Streamlit 页面输入查询词
2. 前端调用 `POST /api/tasks`
3. 后端创建 mock 任务并异步处理
4. 前端轮询任务状态
5. 任务完成后获取结构化文档列表
6. 前端展示摘要、标签、原文链接、PDF 下载入口

## 核心接口

### `POST /api/tasks`

创建任务。

示例请求：

```json
{
  "query": "NVDA",
  "query_type": "stock"
}
```

### `GET /api/tasks/{task_id}`

查询任务状态、进度和结果数量。

### `GET /api/tasks/{task_id}/documents`

获取任务产出的文档列表。

## 后续演进建议

- 用 PostgreSQL 替换内存仓库
- 用 Redis 或消息队列替换本地异步模拟
- 接入真实爬虫和解析器
- 将 Streamlit 替换为小程序或 Web 前端
- 增加用户体系、收藏、订阅和推送能力
