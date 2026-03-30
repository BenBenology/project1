# 自动爬取财报和文章炒股小程序方案

## 1. 需求重写

做一个面向个人投资决策的小程序，用户输入想关注的行业、公司、机构或主题后，系统可以自动抓取公开可获取的财报、新闻、研报和深度文章，对内容进行去重、分类、按时效排序，并提供摘要、原文/PDF 下载与统一查看入口，帮助用户在较短时间内完成信息收集和初步研判，而不是手动在多个网站之间反复搜索。

## 2. MVP 范围

MVP 只解决“高效收集和整理公开投资信息”这个核心问题，不直接做自动交易、不做复杂量化模型、不做社区功能。

- 支持用户输入股票代码、公司名、行业关键词
- 抓取公开网页文章与上市公司财报链接
- 对结果做去重、分类、时间排序
- 展示标题、来源、发布时间、摘要、原文链接
- 对可下载的财报提供 PDF 下载入口
- 提供简单搜索记录与结果列表页
- 支持 10 分钟内完成一次任务并返回结果

不放入 MVP 的内容：

- 自动买卖股票
- 多账户体系和社交分享
- 复杂推荐算法
- K 线、行情、交易信号系统
- 高级舆情评分和情感分析
- 多语言全球市场覆盖

## 3. 功能列表（按优先级排序）

### P0

- 关键词/公司/股票代码输入
- 抓取任务创建与执行
- 财报与文章抓取
- 数据清洗、去重、分类
- 结果列表展示
- 原文跳转与 PDF 下载
- 按发布时间和来源筛选

### P1

- 内容摘要生成
- 抓取失败重试
- 搜索历史记录
- 收藏与标记重点文章
- 定时任务，每天自动更新一次

### P2

- 基于用户关注列表的订阅推送
- 简单情绪倾向分析
- 公司画像页
- 多维度标签，例如“财报/新闻/观点/政策”

## 4. 技术栈建议

### 当前 Demo 前端

- `Streamlit`
- 理由：开发速度快，适合先验证“输入查询词 -> 创建任务 -> 返回结果”的主流程
- 目标：先验证产品链路和结果结构，不在这一阶段追求正式小程序体验

### 后续正式前端

- `uni-app` 或 `Taro`
- 理由：后续可适配微信小程序和 H5，便于把当前 API 直接复用到正式前端
- 原则：前后端继续解耦，替换前端时不重写后端业务逻辑

### 后端

- `Python + FastAPI`
- 理由：适合快速搭建 API、任务编排和原型验证，开发效率高，文档和类型定义也比较清晰
- 当前阶段：优先保持代码简单、可运行、易替换

### 爬取与内容处理

- 当前实现：`requests` + `BeautifulSoup` + source/crawler registry
- 已接入来源：`SEC EDGAR`、`Google News RSS`、`Tesla Investor Relations`
- PDF/附件处理：当前以原始 PDF / filing 链接为主，后续可接对象存储或本地缓存

### 数据存储

- 当前 Demo：内存存储
- 正式版主库：`PostgreSQL`
- 正式版缓存/队列：`Redis`
- 文件存储：`S3` 兼容对象存储或本地临时存储

### AI 能力

- 摘要与分类：接入 LLM API
- 用途：生成文章摘要、提炼重点、统一标签

### 运维部署

- Docker
- Nginx
- 云服务器 + 对象存储
- 监控：基础日志 + 错误告警

## 5. 项目目录结构

```text
project/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI 路由层
│   │   ├── core/               # 配置层
│   │   ├── models/             # 数据模型
│   │   ├── repositories/       # 存储层
│   │   └── services/           # 业务逻辑层
├── frontend/
│   └── streamlit_app.py        # Demo 前端
├── docs/
│   ├── product/                # 产品文档
│   ├── api/                    # 接口文档
│   └── crawler-sources/        # 站点接入说明
├── .env.example
├── requirements.txt
└── README.md
```

## 6. 开发里程碑

### Day 1

- 明确目标用户和使用流程
- 设计任务、文档、附件的核心数据结构
- 搭建 `FastAPI + Streamlit` 基础工程
- 完成“关键词提交抓取任务”接口
- 用 mock 数据跑通最小可用链路

### Day 2

- 完成结果列表页展示和任务状态轮询
- 补齐摘要、标签、附件的统一结构
- 实现 PDF 下载入口
- 补充项目文档、架构文档和任务清单
- 输出一个可演示的本地 demo

### Day 3

- 抽象 crawler 接口，为真实数据接入留口
- 增加统一错误响应和基础日志
- 接入 1 到 2 个公开数据源并跑通
- 做一轮端到端手工测试
- 确认下一阶段从 mock 切到真实数据

## 7. 主要风险和规避方案

### 1. 数据源反爬或访问限制

- 风险：部分站点会限制频繁抓取，导致任务失败
- 规避：优先接入公开 RSS、公告站、官方 IR 页面；控制抓取频率；做失败重试和来源降级；保留 source 级调试能力

### 2. 法律与合规风险

- 风险：直接抓取和存储第三方内容可能涉及版权、服务条款限制
- 规避：优先保存摘要、标题、链接和公开 PDF 地址；避免大规模全文转载；对每个数据源单独评估使用规则

### 3. 内容质量不稳定

- 风险：抓到的文章可能噪声高、重复多、与投资价值弱相关
- 规避：建立来源白名单；做关键词过滤、去重、标签分类；人工先验证高价值来源

### 4. 返回时间过长

- 风险：用户希望快速看到结果，但实时抓取可能超过可接受时长
- 规避：使用异步任务队列；优先返回第一批结果；对热门公司做预抓取和缓存

### 5. 摘要和分类不准确

- 风险：AI 可能误读财报或给出不稳定摘要
- 规避：保留原文链接；摘要仅作辅助；重要字段采用规则提取优先，AI 只做补充

### 6. 用户误以为系统能直接给买卖建议

- 风险：产品定位模糊会让用户期待“自动炒股”
- 规避：明确产品是“信息收集与研判辅助工具”，不是自动投顾或交易系统

## 8. PRD（产品需求文档）

### 8.1 产品定位

这是一款面向个人投资者的信息收集型小程序，核心价值不是替用户直接做交易决策，而是替用户自动完成“找财报、找文章、做初步整理”的重复劳动，缩短从“想研究一家公司”到“拿到可读资料列表”的时间。

### 8.2 目标用户

- 有明确股票研究需求的个人投资者
- 需要快速查看某家公司最新财报和相关文章的用户
- 没有时间长期手动搜集资料的轻研究型用户

### 8.3 用户痛点

- 财报、新闻、研报分散在不同网站
- 手动搜索效率低，容易遗漏重要资料
- 搜到的内容重复多、质量不稳定
- 很难快速区分“官方披露”与“二手解读”

### 8.4 产品目标

#### 核心目标

- 用户输入一个主题后，可在 10 分钟内拿到一批结构化结果
- 结果覆盖财报、公告、新闻、深度文章等主要信息类型
- 用户可直接打开原文或下载 PDF

#### 阶段目标

- 第 1 阶段：跑通抓取、整理、展示闭环
- 第 2 阶段：加入摘要、收藏、订阅更新
- 第 3 阶段：加入更强的标签化与公司研究视图

### 8.5 核心使用场景

#### 场景 1：研究某家公司

用户输入公司名或股票代码，例如“英伟达”或“NVDA”，系统返回最近财报、相关新闻、行业分析文章和官方链接。

#### 场景 2：研究某个行业

用户输入“AI 芯片”“新能源车”“银行”这类行业词，系统返回对应主题下的重点公司财报和相关文章。

#### 场景 3：查看最新更新

用户对某家公司建立关注后，每天自动看到新增的财报或文章。

### 8.6 MVP 业务流程

1. 用户输入关键词、公司名或股票代码
2. 系统创建抓取任务
3. 抓取模块从配置好的数据源收集网页和 PDF 链接
4. 解析模块提取标题、来源、时间、正文摘要、附件信息
5. 系统进行去重、分类、排序
6. 前端展示结果列表
7. 用户查看详情、跳转原文或下载 PDF

### 8.7 页面结构

#### 1. 首页

- 搜索框
- 热门搜索
- 历史搜索
- 最近更新入口

#### 2. 任务结果页

- 任务状态：抓取中、已完成、部分失败
- 结果总数
- 分类筛选：财报、公告、新闻、深度文章
- 排序方式：最新优先、来源优先
- 结果卡片列表

#### 3. 内容详情页

- 标题
- 来源
- 发布时间
- 标签
- 摘要
- 原文链接
- PDF 下载按钮

#### 4. 我的关注页（P1）

- 已关注公司/主题
- 最近更新内容
- 收藏内容

### 8.8 关键交互要求

- 搜索提交后立即创建任务并返回任务编号
- 若抓取未完成，前端展示加载状态并轮询任务进度
- 结果页优先展示已完成部分，不必等待全部抓完
- 财报类内容需突出 PDF 和官方来源
- 同一篇内容重复出现时只保留一条，并展示最佳来源

### 8.9 内容分类规则

- 财报：年报、季报、半年报、10-K、10-Q、业绩公告
- 公告：公司公告、投资者关系文件、电话会纪要
- 新闻：媒体快讯、公司相关新闻
- 深度文章：研报、评论、长文分析

### 8.10 成功指标

#### MVP 指标

- 单次任务平均返回时间小于 10 分钟
- 单次搜索至少返回 10 条有效结果
- 财报类搜索结果命中率达到可用水平
- PDF 下载可用率高于 95%

#### 行为指标

- 搜索后结果查看率
- 原文点击率
- PDF 下载率
- 次日再次使用率

### 8.11 非功能要求

- 系统支持异步任务执行
- 抓取失败不影响已完成结果展示
- 对同一关键词任务支持缓存和复用
- 对来源站点配置限频机制
- 敏感日志不落库，不暴露用户隐私数据
- 支持 source 级状态观测与排障

## 9. 数据库表设计

### 9.1 设计原则

- 先满足 MVP，表数量控制在必要范围
- 抓取任务、原始内容、解析结果、用户行为分层存储
- 尽量支持未来扩展到订阅、推送、管理后台

### 9.2 核心表清单

- `users`：用户表
- `search_tasks`：搜索/抓取任务表
- `sources`：数据源配置表
- `documents`：文章和财报主表
- `document_attachments`：PDF 和附件表
- `document_summaries`：AI 摘要与标签表
- `user_favorites`：用户收藏表
- `user_watchlist`：用户关注表

### 9.3 表结构建议

#### 1. users

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| open_id | varchar(64) | 小程序用户唯一标识 |
| nickname | varchar(64) | 用户昵称 |
| avatar_url | varchar(255) | 头像 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### 2. search_tasks

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| user_id | bigint | 用户 ID，可为空 |
| query | varchar(255) | 搜索词 |
| query_type | varchar(32) | company / stock / industry / topic |
| status | varchar(32) | pending / running / success / partial_success / failed |
| progress | int | 0-100 进度 |
| result_count | int | 结果数 |
| started_at | timestamp | 开始时间 |
| finished_at | timestamp | 完成时间 |
| error_message | text | 错误信息 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### 3. sources

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| name | varchar(100) | 来源名称 |
| base_url | varchar(255) | 来源域名 |
| source_type | varchar(32) | official / news / research / aggregator |
| enabled | boolean | 是否启用 |
| priority | int | 优先级 |
| rate_limit_per_min | int | 每分钟限频 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### 4. documents

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| task_id | bigint | 来源任务 ID |
| source_id | bigint | 数据源 ID |
| doc_type | varchar(32) | report / filing / news / article |
| title | varchar(500) | 标题 |
| company_name | varchar(255) | 公司名 |
| stock_code | varchar(64) | 股票代码 |
| publish_time | timestamp | 发布时间 |
| author | varchar(255) | 作者/机构 |
| source_name | varchar(100) | 来源名称冗余字段 |
| url | text | 原文链接 |
| content_text | text | 清洗后的正文，可选 |
| language | varchar(16) | 语言 |
| dedupe_hash | varchar(128) | 去重哈希 |
| crawl_status | varchar(32) | crawled / parsed / failed |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### 5. document_attachments

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| document_id | bigint | 文档 ID |
| file_type | varchar(32) | pdf / xls / html |
| file_name | varchar(255) | 文件名 |
| file_url | text | 原始文件链接 |
| storage_url | text | 存储后的地址 |
| file_size | bigint | 文件大小 |
| download_status | varchar(32) | pending / success / failed |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### 6. document_summaries

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| document_id | bigint | 文档 ID |
| summary_text | text | 摘要 |
| key_points | jsonb | 重点提炼 |
| sentiment | varchar(16) | positive / neutral / negative |
| tags | jsonb | 标签列表 |
| model_name | varchar(64) | 使用的模型 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### 7. user_favorites

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| document_id | bigint | 文档 ID |
| created_at | timestamp | 创建时间 |

#### 8. user_watchlist

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| keyword | varchar(255) | 关注关键词 |
| keyword_type | varchar(32) | company / stock / industry / topic |
| enabled | boolean | 是否启用 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 9.4 索引建议

- `search_tasks(query, created_at)`
- `documents(dedupe_hash)`
- `documents(stock_code, publish_time)`
- `documents(company_name, publish_time)`
- `documents(doc_type, publish_time)`
- `document_attachments(document_id)`
- `user_favorites(user_id, document_id)`
- `user_watchlist(user_id, keyword)`

### 9.5 关系说明

- 一个 `search_task` 可以产生多条 `documents`
- 一条 `document` 可以有多个 `document_attachments`
- 一条 `document` 对应一条或多条摘要记录，MVP 可先按一条处理
- 一个用户可以有多个收藏和多个关注项

## 10. 接口草案

### 10.1 提交抓取任务

- `POST /api/tasks`
- 入参：
  - `query`
  - `queryType`
- 出参：
  - `taskId`
  - `status`

### 10.2 查询任务状态

- `GET /api/tasks/:taskId`
- 返回任务状态、进度、结果数、错误信息

### 10.3 获取结果列表

- `GET /api/tasks/:taskId/documents`
- 支持参数：
  - `docType`
  - `sortBy`
  - `page`
  - `pageSize`

### 10.4 获取 source 执行结果

- `GET /api/tasks/:taskId/sources`
- 返回每个 source 的状态、结果数和错误信息

### 10.5 获取内容详情

- `GET /api/documents/:id`
- 返回标题、来源、发布时间、摘要、标签、原文链接、附件信息

### 10.6 收藏内容

- `POST /api/favorites`
- 入参：
  - `documentId`

### 10.7 获取关注列表

- `GET /api/watchlist`

### 10.8 新增关注项

- `POST /api/watchlist`
- 入参：
  - `keyword`
  - `keywordType`
