# hs-dev-skill: 产品开发 Skill

> **文档驱动开发（DDD） + 六元组标准化运行时 + Agent 上下文引擎**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/tests/)
[![Spec Version](https://img.shields.io/badge/spec-v2.4-blue.svg)](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/spec_v2_4.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/LICENSE)

`hs-dev-skill` 是专为 AI Agent 和现代研发团队打造的标准化产品开发技能包。它建立了以文档为核心驱动力、以六元组为业务签名规范、以渐进式 JSONL 索引为检索底座的高可靠研发闭环。

---

## 🌟 核心特性

1. **渐进式四级索引路由（Progressive JSONL Indexing）**：
   - 杜绝全文盲目扫描，按 `根索引 -> 域索引 -> 模块索引 -> 精确切片` 精准注入上下文，极大节省 Token 预算。
2. **六元组标准化架构（Six-Tuple Architecture）**：
   - `exception method(input, output, context, isolate, metrics, recall)`
   - 全面覆盖：业务主逻辑、Saga 事务补偿、异常熔断降级、可观测性度量、异步回调。
3. **任务生命周期三文件强一致性（Triple-File Consistency）**：
   - `_00_task.idx`（主索引）+ `_01_task_brief/`（15行紧凑滚动清单）+ `_02_task_detail/`（详细执行记录）原子同步与会话交接（Session Handoff）。
4. **数据库设计与迁移原子同步（Atomic Migration Sync）**：
   - 设计文档、前向迁移脚本（`V...sql`）与回滚脚本（`U...sql`）强制原子同步，杜绝 SQL 保留关键字冲突（如禁止直接使用 `desc`）。
5. **Mock 契约与业务代码完全解耦**：
   - 生产代码零污染，通过 Test Profile 灵活组合测试数据集、错误注入与延迟注入。
6. **全自动化门禁自检工具链**：
   - 内置 CLI 工具支持一键初始化、索引防漂移校验、三文件一致性比对与死代码扫描。

---

## 🚀 快速上手与常用命令

### 1. 安装与依赖
环境要求：`Python >= 3.8`

### 2. 快捷 Makefile 命令
```bash
# 执行自动化单元测试
make test

# 执行提交前全量门禁自检
make verify

# 死代码与孤儿方法扫描
make scan-dead-code

# 初始化当前工作区文档骨架
make init-docs
```

### 3. CLI 工具直接调用
```bash
# 1. 初始化项目文档树与索引
python3 scripts/init_hs_dev_docs.py --root .

# 2. 创建新研发任务
python3 scripts/task_manager.py create --id order_create --title "创建交易订单" --owner "agent" --priority "P0"

# 3. 推进任务状态
python3 scripts/task_manager.py status --id order_create --set IN_PROGRESS
python3 scripts/task_manager.py status --id order_create --set VERIFYING
python3 scripts/task_manager.py status --id order_create --set COMPLETED

# 4. 校验全量一致性与门禁
python3 scripts/verify_consistency.py --root .
```

---

## 📚 目录体系与文档指引

- **[SKILL.md](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/SKILL.md)**：Agent 核心技能定义与执行手册
- **[references/](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/)**：
  - [规格定义书 v2.4 正式版](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/spec_v2_4.md)
  - [六元组标准化运行时指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/six_tuple_runtime.md)
  - [渐进式四级索引路由指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/four_level_routing.md)
  - [任务状态机与生命周期指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/task_state_machine.md)
  - [Mock 规范与契约测试指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/mock_contract_guide.md)
  - [全层级质量门禁指南](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/references/quality_gates.md)
- **[resources/templates/](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/resources/templates/)**：设计文档、词典、迁移、Profile 预置脚手架模板
- **[examples/](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/examples/)**：[订单服务全流程参考用例](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/examples/order_service/)
