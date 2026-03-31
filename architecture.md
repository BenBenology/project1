# 系统架构说明

这个文档描述当前 MVP 的架构设计，以及后续如何从 mock 演进到真实系统。

## 1. 架构目标

当前架构的核心目标有三个：

- 先跑通“提交查询 -> 获取结果”的主流程
- 保持前后端解耦，方便未来替换成小程序
- 为真实爬虫、数据库、摘要服务预留演进空间

## 2. 当前架构总览

```text
[Streamlit Frontend]
        |
        v
[FastAPI API Layer]
        |
        v
[Task Service]
        |
        +--> [SQLite Repository]
        |
        +--> [Source Repository]
        |
        +--> [Market Data Gateway]
                 |
                 +--> [MCP Client] ----> [Market Data MCP Server]
                 |                           |
                 |                           +--> [Crawler Registry]
                 |
                 +--> [Local Crawler Fallback]
```

## 3. 分层说明

### 3.1 前端层

文件位置：

- `frontend/streamlit_app.py`

职责：

- 提供查询输入界面
- 调用后端接口
- 轮询任务状态
- 展示结构化结果

设计原则：

- 前端不写业务规则
- 前端不感知 mock 或真实数据实现
- 后续替换为小程序时，只保留 API 调用模式

### 3.2 API 路由层

文件位置：

- `backend/app/api/routes/`

职责：

- 接收请求
- 参数校验
- 返回标准响应

设计原则：

- 路由层尽量薄
- 不在路由层写复杂业务逻辑

### 3.3 服务层

文件位置：

- `backend/app/services/`

职责：

- 管理任务生命周期
- 组织真实 source 与 crawler 的调度流程
- 控制任务状态变化
- 汇总 source 级成功/失败信息
- 通过 gateway 选择本地 crawler 或 MCP 运行时

设计原则：

- 所有业务编排都集中在服务层
- 后续接入真实 crawler 时优先改服务层，不改前端

### 3.4 仓储层

文件位置：

- `backend/app/repositories/`

职责：

- 保存任务数据
- 保存文档结果
- 保存每个 source 的执行结果

当前实现：

- 使用 SQLite 持久化任务、文档和来源配置

未来演进：

- 替换为 PostgreSQL
- 如果要支持异步任务和缓存，可接 Redis

### 3.5 适配层

文件位置：

- `backend/app/adapters/`

职责：

- 统一 FastAPI 到 MCP 的调用方式
- 在 MCP 不可用时自动回落到本地 crawler
- 隔离 JSON-RPC/TCP 细节，避免污染业务层

### 3.6 MCP 层

文件位置：

- `mcp/market_data_server/`

职责：

- 统一外部数据获取能力
- 提供工具化接口，供后端或其他 agent 复用
- 承担未来的并发控制、缓存、重试、限流职责

### 3.5 数据模型层

文件位置：

- `backend/app/models/`

职责：

- 定义请求结构
- 定义任务结构
- 定义文档结构
- 保证前后端数据格式稳定

## 4. 当前主流程时序

1. 用户在 Streamlit 输入查询词
2. 前端调用 `POST /api/tasks`
3. FastAPI 创建任务并返回 `task_id`
4. 后端后台任务模拟处理
5. 服务层根据启用的 sources 调用 market data gateway
6. gateway 优先尝试 MCP，失败时回落到本地 crawler
7. 后端记录每个 source 的执行结果
8. 前端轮询 `GET /api/tasks/{task_id}`
9. 任务完成后调用 `GET /api/tasks/{task_id}/documents`
10. 如需排障，可调用 `GET /api/tasks/{task_id}/sources`
11. 前端展示结果

## 6. 后续演进架构

后续建议演进为：

```text
[Mini Program / Web Frontend]
            |
            v
      [FastAPI API]
            |
            v
      [Task Orchestrator]
             |
             v
     [Market Data Gateway]
        /             \
       v               v
[Local Fallback]   [MCP Server]
                        |
                        v
               [Crawler / Parser / Cache]
                        |
                        v
                   [PostgreSQL / Redis / PDF]
```

## 7. 关键替换点

### 替换前端

- 保留 API 不变
- 用小程序或 Web 前端替换 Streamlit

### 替换 mock 数据

- 保留 `TaskService` 和 `Crawler Registry` 主流程
- 将 mock crawler 逐步替换成真实 crawler 和 parser

### 替换内存仓库

- 保留 repository 接口
- 用数据库实现替换当前内存实现

## 8. 当前限制

- SEC 在部分网络环境下可能出现 SSL 失败
- 当前公司资料 fallback 已覆盖一批高频美股公司，并为 Tesla 提供额外季度材料与 PDF
- MCP 目前还是项目内自定义 JSON-RPC/TCP skeleton，尚未接入你现有的外部 MCP 基础设施
- 没有用户登录态
- 没有权限控制
- 没有生产环境部署能力

## 9. 架构判断标准

如果后续新增功能满足以下条件，就说明架构方向是对的：

- 不需要重写前端主流程
- 不需要重写路由协议
- 新增真实抓取逻辑时只主要改服务层和仓储层
- 可以逐步从 demo 演进到正式系统
