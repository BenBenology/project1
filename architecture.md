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
        +--> [In-Memory Repository]
        |
        +--> [Mock Data Builder]
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
- 组织 mock 数据或未来真实抓取流程
- 控制任务状态变化

设计原则：

- 所有业务编排都集中在服务层
- 后续接入真实 crawler 时优先改服务层，不改前端

### 3.4 仓储层

文件位置：

- `backend/app/repositories/`

职责：

- 保存任务数据
- 保存文档结果

当前实现：

- 使用内存存储

未来演进：

- 替换为 PostgreSQL
- 如果要支持异步任务和缓存，可接 Redis

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
5. 服务层生成 mock 文档
6. 前端轮询 `GET /api/tasks/{task_id}`
7. 任务完成后调用 `GET /api/tasks/{task_id}/documents`
8. 前端展示结果

## 5. 为什么当前不用数据库

这是一个合理的阶段性取舍，不是偷懒。

原因：

- 当前目标是验证产品主链路
- 数据库会增加初始化和迁移成本
- 在还没接入真实爬虫前，内存存储足够支撑 demo

但这个取舍的前提是：

- 仓储层已经独立
- 后续替换为数据库时不需要重写 API

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
       /       |       \
      v        v        v
[Crawler]  [Parser]  [AI Summary]
      \        |        /
            v
      [PostgreSQL]
            |
            v
          [Redis]
            |
            v
     [Object Storage / PDF]
```

## 7. 关键替换点

### 替换前端

- 保留 API 不变
- 用小程序或 Web 前端替换 Streamlit

### 替换 mock 数据

- 保留 `TaskService` 主流程
- 将 `Mock Data Builder` 替换成真实 crawler 和 parser

### 替换内存仓库

- 保留 repository 接口
- 用数据库实现替换当前内存实现

## 8. 当前限制

- 任务状态保存在内存中，服务重启后会丢失
- 没有真实站点抓取
- 没有用户登录态
- 没有权限控制
- 没有生产环境部署能力

## 9. 架构判断标准

如果后续新增功能满足以下条件，就说明架构方向是对的：

- 不需要重写前端主流程
- 不需要重写路由协议
- 新增真实抓取逻辑时只主要改服务层和仓储层
- 可以逐步从 demo 演进到正式系统
