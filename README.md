# hs-dev-skill: 产品开发 Skill

> **文档驱动开发（DDD） + 六元组标准化运行时 + Agent 上下文引擎**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/tests/)
[![Spec Version](https://img.shields.io/badge/spec-v2.8-blue.svg)](references/spec_v2_4.md)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](references/cross_platform.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/LICENSE)

`hs-dev-skill` 是专为 AI Agent 和现代研发团队打造的标准化产品开发技能包，**可在 Windows / Linux / macOS 三端运行**。它建立了以文档为核心驱动力、以六元组为业务签名规范、以渐进式 JSONL 索引为检索底座的高可靠研发闭环；并以**置信度决策 + 偏好记忆 + GitHub 高星对标**约束交互——通用方案与用户偏好自主推进，模糊新技术/UI 先学成熟项目，仅在项目特有且选项难分高下时询问开发者。

---

## 🌟 核心特性

1. **置信度决策（Confidence-Gated Decision）**：
   - 大家通用的解决方案不询问；仅当影响面广、项目特有、既有资料未提及、且多种选择置信接近时，才结构化询问并由开发者决策。详见 [confidence_decision.md](references/confidence_decision.md)。
2. **技术学习与偏好记忆 + GitHub 高星对标（全局共享）**：
   - 落盘于用户主目录 `~/.hs-dev-skill/`（偏好 `preferences.yaml`、笔记 `tech_learning/`），**所有项目共用**；模糊新技术/UI 优先检索 GitHub 高 Star 成熟方案。初始化：`python3 scripts/init_hs_global.py`。详见 [learn_and_prefer.md](references/learn_and_prefer.md)。
3. **渐进式四级索引路由（Progressive JSONL Indexing）**：
   - 杜绝全文盲目扫描，按 `根索引 -> 域索引 -> 模块索引 -> 精确切片` 精准注入上下文，极大节省 Token 预算。
4. **六元组标准化架构（Six-Tuple Architecture）**：
   - `exception method(input, output, context, isolate, metrics, recall)`
   - 全面覆盖：业务主逻辑、Saga 事务补偿、异常熔断降级、可观测性度量、异步回调。
5. **任务生命周期三文件强一致性（Triple-File Consistency）**：
   - `_00_task.idx`（主索引）+ `_01_task_brief/`（15行紧凑滚动清单）+ `_02_task_detail/`（详细执行记录）原子同步与会话交接（Session Handoff）。
6. **数据库设计与迁移原子同步（Atomic Migration Sync）**：
   - 设计文档、前向迁移脚本（`V...sql`）与回滚脚本（`U...sql`）强制原子同步，杜绝 SQL 保留关键字冲突（如禁止直接使用 `desc`）。
7. **Mock 契约与业务代码完全解耦**：
   - 生产代码零污染，通过 Test Profile 灵活组合测试数据集、错误注入与延迟注入。
8. **全自动化门禁自检工具链**：
   - 内置 CLI 工具支持一键初始化、索引防漂移校验、三文件一致性比对与死代码扫描。
9. **默认止于本地 Commit；明确要求才推送**：
   - Agent 常规只做门禁 + 本地提交；**仅当用户明确说要推送**时才代为 `git push`。

---

## 🚀 快速上手与常用命令

### 1. 安装与依赖
- 环境要求：`Python >= 3.8`
- **支持平台**：Windows / Linux / macOS（详见 [cross_platform.md](references/cross_platform.md)）
- 解释器：`python3`（Linux/macOS）、`python` 或 `py -3`（Windows）

### 2. 快捷 Makefile 命令
```bash
# 查看当前 OS 解析出的全局路径
make paths
# Windows 若默认 python 不对： make paths PYTHON="py -3"

make test
make verify
make scan-dead-code
make init-docs
make init-global
```

无 make 时直接用下一节的 Python 命令即可。

### 3. CLI 工具直接调用
```bash
# 打印全局路径（三端）
python scripts/hs_paths.py

# 0. 初始化跨项目全局共享区（偏好 + 技术学习）
python scripts/init_hs_global.py

# 1. 初始化项目文档树与索引
python scripts/init_hs_dev_docs.py --root .

# 2. 创建新研发任务
python scripts/task_manager.py create --id order_create --title "创建交易订单" --owner "agent" --priority "P0"

# 3. 推进任务状态
python scripts/task_manager.py status --id order_create --set IN_PROGRESS
python scripts/task_manager.py status --id order_create --set VERIFYING
python scripts/task_manager.py status --id order_create --set COMPLETED

# 4. 校验全量一致性与门禁
python scripts/verify_consistency.py --root .
```

---

## 📚 目录体系与文档指引

- **[SKILL.md](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/SKILL.md)**：Agent 核心技能定义与执行手册
- **[references/](references/)**：
  - [跨平台支持（Windows / Linux / macOS）](references/cross_platform.md)
  - [置信度决策协议](references/confidence_decision.md)
  - [技术学习、偏好记忆与 GitHub 对标](references/learn_and_prefer.md)
  - [全生命周期驱动引擎指南](references/spec_driven_lifecycle.md)
  - [规格定义书 v2.4 正式版](references/spec_v2_4.md)
  - [六元组标准化运行时指南](references/six_tuple_runtime.md)
  - [渐进式四级索引路由指南](references/four_level_routing.md)
  - [任务状态机与生命周期指南](references/task_state_machine.md)
  - [Mock 规范与契约测试指南](references/mock_contract_guide.md)
  - [全层级质量门禁指南](references/quality_gates.md)
- **[resources/templates/](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/resources/templates/)**：设计文档、词典、迁移、Profile 预置脚手架模板
- **[examples/](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/examples/)**：[订单服务全流程参考用例](file:///home/hardstone/CodeSpace/GitHub/hs-dev-skill/examples/order_service/)
