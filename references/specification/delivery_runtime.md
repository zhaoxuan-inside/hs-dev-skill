# 3. Git 提交信息规范

**何时读**：处理3. Git 提交信息规范时；先沿用[入口公共约束](../spec_v2_4.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 3. Git 提交信息规范

### 3.1 提交信息格式

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 type 类型

| type | 含义 |
|---|---|
| feat | 新增功能 |
| fix | 修复缺陷 |
| docs | 文档变更 |
| style | 格式调整，不影响逻辑 |
| refactor | 重构，不新增功能不修复缺陷 |
| perf | 性能优化 |
| test | 测试相关 |
| build | 构建、依赖、脚本变更 |
| chore | 杂项，不影响 src 与 test |
| revert | 回滚 |
| spec | 设计文档、接口、方法、DB、调用链变更 |
| migrate | 数据库迁移脚本变更 |
| mock | Mock 服务、Mock 数据、测试集配置变更 |

### 3.3 提交与推送边界（强制）

- 常规流程：Agent 在门禁通过后执行**本地** `git commit`，**不主动**推送。
- **仅当用户明确要求推送**（如「推送代码」「帮我 push」「push 到远程」）时，Agent 可代为执行 `git push`（含首次 `-u`）并回报结果。
- 未获明确推送授权时，禁止 `git push` / 等价远程推送。

---

## 4. 全层级质量保障机制

| 层级 | 范围 | 门禁 |
|---|---|---|
| `_00_e2e` | 端到端全链路 | 冒烟全通过，覆盖主流程与致命错误 |
| `_01_method_test` | 方法级单元测试 | 核心域业务逻辑分支覆盖率 ≥ 85%，核心方法降级与补偿分支 100% 覆盖 |
| `_02_integration_test` | DB、缓存、中间件联调 | 事务原子性、补偿生效、超时熔断 |
| `_03_contract_test` | 前后端/多端协议 | 字段增删改必须静态比对与协议断言 |
| `_04_regression_test` | 回归 | 历史缺陷用例全通过 |
| `_05_performance_test` | 性能 | 基准达标，无退化 |
| `_06_security_test` | 安全 | 注入、越权、脱敏、密钥检查 |
| `_07_compatibility_test` | 兼容 | 浏览器、OS、设备、版本矩阵 |
| `_08_test_data` | 测试数据 | 脱敏、可重复、可清理 |

---

## 5. Mock 规范

1. 业务代码中严禁包含 Mock 桩、Mock 分支、测试数据硬编码；
2. Mock 必须作为独立服务启动，通过接口或网络层接入；
3. Mock 代码与 Mock 数据必须分离；
4. Mock 契约必须与 `_04_engineering_contract/_02_interface_design`、`_03_contract_test` 保持一致；
5. 测试集通过 profile 组合，不改代码即可切换数据、场景、错误与延迟；
6. Mock 契约单一真理源位于 `hs_dev_docs/_04_engineering_contract/_03_mock_contract/`。

---

## 6. Skill 执行引擎运行时机制

### 6.1 `.idx` 索引文件规范（JSONL）

`.idx` 统一采用 **JSONL（JSON Lines）** 格式：每行一个独立 JSON 对象。

首行为元数据行，包含 `version`、`category`、`root`；其余每行为一个索引条目。

```jsonl
{"version":"1.0","category":"interface","root":"_04_engineering_contract/_02_interface_design"}
{"id":"order_create","title":"创建订单与锁库","path":"_04_engineering_contract/_02_interface_design/_01_order/_01_order_create_design.md","digest":"a1b2c3d4","status":"active"}
{"id":"order_cancel","title":"取消订单","path":"_04_engineering_contract/_02_interface_design/_01_order/_02_order_cancel_design.md","digest":"e5f6g7h8","status":"active"}
```

### 6.2 渐进式四级路由体系

1. **一级（根索引）**：读 `hs_dev_docs/_00_hs_dev_docs.idx` 定位功能域；
2. **二级（域索引）**：读 `_0N_{domain}/_00_{domain}.idx` 定位子模块；
3. **三级（模块索引）**：读 `_00_{model_name}_{domain}.idx` 锁定目标文档；
4. **四级（精确注入）**：仅注入目标文档精确章节/行号。

### 6.3 任务三文件一致性约束

- `task_id` 为唯一主键。
- `_05_task_orchestration/` 下的 `_00_task.idx`、`_01_task_brief/`、`_02_task_detail/` 中的 `task_id`、`title`、`status`、`updated` 必须一致。
- 变更顺序：先改 `task_detail`，再同步 `task_brief`，最后更新 `task.idx`。
