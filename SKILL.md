---
name: hs-dev-skill
description: >-
  标准化文档驱动开发（DDD）与六元组架构执行引擎。提供渐进式四级索引（JSONL）检索、任务生命周期强一致性（三文件状态机）、六元组方法（主逻辑/降级/补偿/度量/回调）、数据库迁移原子同步（V/U）、Mock契约隔离以及全层级质量门禁自检。当用户进行产品开发、领域建模、重构、编写六元组业务逻辑或需要初始化 hs_dev_docs 规范体系时使用此技能。
---

# 产品开发 Skill (hs-dev-skill)

版本：v2.4  
核心定位：**文档驱动开发（DDD） + 六元组标准化运行时 + Agent 上下文引擎**

---

## 1. 核心能力与工具箱 (CLI Tooling)

本 Skill 内置了完整的自动化工具链，位于 [scripts/](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/) 目录下：

| 工具脚本 | 功能职责 | 常用命令示例 |
|---|---|---|
| [`init_hs_dev_docs.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/init_hs_dev_docs.py) | 一键初始化或对齐完整项目骨架与 JSONL 索引 | `python3 scripts/init_hs_dev_docs.py --root .` |
| [`idx_manager.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/idx_manager.py) | JSONL `.idx` 索引增删改查、哈希防漂移校验 | `python3 scripts/idx_manager.py verify hs_dev_docs/_00_hs_dev_docs.idx` |
| [`task_manager.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/task_manager.py) | 任务创建、状态机流转、三文件强一致性同步与会话交接 | `python3 scripts/task_manager.py create --id order_create --title "创建订单"`<br>`python3 scripts/task_manager.py status --id order_create --set IN_PROGRESS` |
| [`verify_consistency.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/verify_consistency.py) | 提交前全量门禁自检（三文件/索引/SQL关键字/迁移脚本） | `python3 scripts/verify_consistency.py --root .` |
| [`dead_code_scanner.py`](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/scripts/dead_code_scanner.py) | 基于调用链拓扑与白名单注解的死代码扫描 | `python3 scripts/dead_code_scanner.py --root .` |

---

## 2. 渐进式四级路由检索 (Progressive Loading)

为避免单次大全文读取耗尽 Token 预算，Agent 必须遵循 **四级路由体系**：

```text
[1. 根索引]  hs_dev_docs/_00_hs_dev_docs.idx (读取目标领域)
      │
[2. 域索引]  hs_dev_docs/_0N_{domain}/_00_{domain}.idx (定位子模块)
      │
[3. 模块索引] hs_dev_docs/_0N_{domain}/_01_{module}/_00_{module}_{domain}.idx (锁定目标文件)
      │
[4. 精确切片] 仅读取目标文件的具体行号范围 (如 view_file 局部读取)
```

详细规范请参阅：[四级路由检索指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/four_level_routing.md)。

---

## 3. 六元组标准化开发范式

在实现任何核心业务方法时，统一遵循六元组标准签名：

```text
exception method_name(input, output, context, isolate, metrics, recall);
exception method_name_fallback(input, output, context, isolate, metrics, recall);
exception method_name_compensate(input, output, context, isolate, metrics, recall);
exception method_name_metrics(input, output, context, isolate, metrics, recall);
exception method_name_recall(input, output, context, isolate, metrics, recall);
```

### 参数约束速查
- `exception`：成功返回 `null`/`None`/`Ok(())`；失败返回标准异常 Map（`code`、`msg`、`retryable`、`details`）。
- `input`：只读业务入参，扁平化键名。
- `output`：业务计算出参容器。
- `context`：运行时追踪与超时（降级/补偿时挂载 `context.last_exception`）。
- `isolate`：只读租户与安全隔离信息。
- `metrics`：度量计时与计数收集器。
- `recall`：异步回调与挂起控制器。

详细指南与多语言代码模式请参阅：[六元组运行时指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/six_tuple_runtime.md)。

---

## 4. 任务状态机与开发闭环流程

```text
DRAFT -> READY -> IN_PROGRESS -> BLOCKED -> VERIFYING -> COMPLETED / ABORTED
```

### 标准执行步骤：

1. **初始态感知**：
   - 检查 `hs_dev_docs/_00_hs_dev_docs.idx`。若项目尚未初始化，运行 `python3 scripts/init_hs_dev_docs.py`。
2. **任务创建与装载**：
   - 执行 `python3 scripts/task_manager.py create --id {task_id} --title "{task_title}"`。
   - 自动生成 `task_detail`、`task_brief`（满10条自动滚动分片）与 `context_pack`。
3. **开发三同步**：
   - 编写/修改业务代码（六元组标准）；
   - 同步更新方法设计、接口设计与表结构设计；
   - 同步生成原子前向/回滚脚本（`V...sql` 与 `U...sql`，**严禁使用 SQL 关键字 `desc`**）；
   - 同步编写全覆盖单元测试与契约测试。
4. **测试与质量门禁验证**：
   - 运行测试用例，确保分支覆盖率 ≥ 85%，降级与补偿分支 100% 覆盖；
   - 执行 `python3 scripts/verify_consistency.py` 确保三文件一致、索引无漂移、迁移无缺失。
5. **任务回写与提交闭环**：
   - 执行 `python3 scripts/task_manager.py status --id {task_id} --set COMPLETED` 自动归档；
   - 按照 Git 规范提交代码（`feat(...)` / `spec(...)` / `migrate(...)` / `mock(...)`）。

---

## 5. 参考规范与模板链接

- [完整规格定义书 v2.4](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/spec_v2_4.md)
- [六元组标准化运行时指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/six_tuple_runtime.md)
- [渐进式四级索引路由指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/four_level_routing.md)
- [任务生命周期与状态机指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/task_state_machine.md)
- [Mock 规范与契约测试指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/mock_contract_guide.md)
- [全层级质量门禁指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/quality_gates.md)
- [订单服务完整参考实现](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/examples/order_service/)
