# 5. 机制四：可观测性与运行时遥测机制 (Observability & Probes)

**何时读**：处理5. 机制四：可观测性与运行时遥测机制 (Observability & Probes)时；先沿用[入口公共约束](../auxiliary_governance.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 5. 机制四：可观测性与运行时遥测机制 (Observability & Probes)

### 5.1 JSON 结构化日志契约
生产环境禁止使用控制台裸字符串 `print` 或 `console.log`，必须统一采用结构化日志记录器，每条日志至少包含以下标准字段：
- `timestamp`：ISO-8601 标准 UTC 时间戳（如 `2026-10-14T09:15:00.000Z`）；
- `level`：日志级别（`DEBUG`, `INFO`, `WARN`, `ERROR`）；
- `trace_id`：全局分布式追踪 ID（由网关生成并在所有微服务间通过 HTTP Header 穿透）；
- `span_id`：当前调用跨度 ID；
- `message`：人类可读事件简述；
- `context`：结构化键值对（如 `user_id`, `order_no`, `duration_ms`）。

### 5.2 标准健康探针规范 (Health Probes)
微服务与后端应用必须提供标准的 HTTP 探针端点：
- `GET /livez` (Liveness)：进程存活探针，返回 `200 OK` 表示主进程未死锁、未崩溃；
- `GET /readyz` (Readiness)：服务就绪探针，检查关键依赖（如数据库连接池、Redis 缓存）是否正常可用，就绪返回 `200`，否则返回 `503` 并切断流量；
- `GET /healthz` (Diagnostics)：健康诊断端点，返回当前系统版本号（符合四段式）、运行耗时、各子模块健康状态摘要。

### 5.3 崩溃堆栈与符号表强绑定归档
移动端（Android/iOS）及桌面端打包时，符号表（Android Proguard `mapping.txt`、iOS `dSYM`、Web/Electron `source-map`）必须与四段式打包版本号绝对一致，并自动归档至 `output/<client>/symbols/`，严禁遗失导致线上崩溃无法还原堆栈。

---

## 6. 机制五：数据韧性与容灾回滚机制 (Data Resilience & DR)

### 6.1 业务容灾目标 (RPO & RTO)
在阶段 2 架构设计文档中，必须明确核心数据存储的容灾指标：
- **RPO (Recovery Point Objective)**：系统遭遇严重故障时允许丢失的最大数据时间范围（如核心交易 RPO < 1 分钟）；
- **RTO (Recovery Time Objective)**：从故障发生到服务完全恢复所需的最大时间（如核心服务 RTO < 15 分钟）。

### 6.2 数据库迁移 V/U 原子配对与备份指引
1. 每一份前向数据库升级脚本 `V{ver}__{desc}.sql` 必须配对 `U{ver}__{desc}.sql` 回滚脚本。
2. 在执行任何涉及 `ALTER TABLE DROP COLUMN`、`TRUNCATE` 或大表重构的 DDL 前，必须在前置步骤中提供物理快照/逻辑备份命令说明。

### 6.3 外部依赖熔断与降级预案 (Circuit Breaker & Fallback)
调用三方依赖（如第三方支付、短信网关、大模型推理 API）时：
- 必须配置合理的超时时间（Timeout）与指数避退重试策略（Exponential Backoff）；
- 必须具备熔断器（连续失败阈值触发熔断，避免级联雪崩）；
- 必须提供降级兜底方案（Fallback），例如返回默认展示、降级走本地缓存或返回友好排队提示。

---
