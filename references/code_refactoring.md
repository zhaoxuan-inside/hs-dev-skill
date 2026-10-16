# 代码重构与演进指南（Code Refactoring & Clean Evolution）

**何时读**：消除坏味道、解耦复杂方法、提炼深模块、迁移引入设计模式、或做性能优化但不改变外部契约时；每会话最多一次。

---

## 1. 核心定义与铁律：零可观测行为漂移

重构（Refactoring）的严格定义是：**在不改变软件外部可观测行为的前提下，改善其内部结构。**  
铁律要求：
1. **测试保护网先决（Safety Net First）**：**没有充分自动化测试覆盖的代码禁止重构**；若测试不足，必须先编写特征测试（Characterization Tests）或快照测试（Golden Master）；
2. **零契约漂移（Zero Contract Drift）**：公共 API、导出函数签名、DB 实体、Event 事件名绝对保持向后兼容；
3. **两顶帽子原则（Two Hats Rule）**：**重构时不增加新功能，增加新功能时不重构**；严禁将重构与功能变更混在一个提交中；
4. **抗方法爆炸与深模块（Deep Module & Deduplication）**：重构目标是让接口更厚实简单、内部更完整聚合；严格执行 `doc_index_db method-search` 杜绝衍生碎片方法。

---

## 2. 重构执行三阶段标准流

```text
[阶段 1: 建立防护网] ──────► [阶段 2: 结构重组与模式落地] ──────► [阶段 3: 行为等价验证与门禁]
 固化输入输出快照测试              消除坏味道 / 提炼深模块 / 引入模式          测试 100% PASS 且 0 行为漂移
```

### 阶段 1：建立行为保护网（Safety Net Construction）
- **识别保护盲区**：评估待重构模块的测试覆盖率；
- **固化特征测试（Characterization Testing）**：
  - 针对复杂历史遗留逻辑，先输入典型参数与边界参数，固化其现有的真实输出快照（即使现有输出有怪癖，也先固化）；
  - 确保保护网测试 100% 运行通过，作为重构期间的“定海神针”。

### 阶段 2：结构重组与模式落地（Structural Restructuring）
- **消除坏味道**：
  - 过长方法（Long Method） $\to$ 按业务内聚点拆分，或采用三段式修改；
  - 霰弹式修改（Shotgun Surgery） $\to$ 聚合至单一深模块（[`deep_modules.md`](deep_modules.md)）；
  - 复杂分支与类型判断 $\to$ 查阅 [`design_patterns.md`](design_patterns.md)，引入策略模式（Strategy）或状态模式（State）；
- **方法意图查重**：在提炼辅助方法前，强制运行：
  ```bash
  python scripts/doc_index_db.py --root . method-search --q "<抽取意图>"
  ```
  若重合度 $\ge 80\%$ 强制复用，严禁产生影子函数。

### 阶段 3：契约同步、索引自愈与行为等价门禁（Contract Sync & Equivalence Verification）
- **运行特征测试**：保护网测试必须一次性全部通过，断言无任何外部可观测行为漂移；
- **清理与固化自动化测试**：将临时快照测试提炼为标准工程单元测试，纳入日常测试集；
- **契约文档与模式档案同步**：
  - 更新 `_04_engineering_contract/_04_method_design/` 中重构后方法的画像属性、符号锚点、局部依赖拓扑及单跑命令；
  - 若引入了设计模式，同步更新 `_03_architecture_design/_02_pattern_clusters/` 模式集群档案；
- **过程账本与快照记录**：在 `_06_dev_process/_01_plan_log` 标记重构步骤为 `done`，`_02_change_log` 记录最终快照；
- **双层索引自愈与罗盘刷新**：
  ```bash
  python scripts/idx_manager.py rebuild
  python scripts/doc_index_db.py --root . rebuild
  python scripts/doc_index_db.py --root . generate-guide
  ```
- **静态检测与门禁硬拦截**：静态分析工具（Linter / TypeChecker / Dead Code Scanner）必须 0 Warning 且 0 Error，运行 `python scripts/verify_consistency.py --root . --strict` 确保零漂移，方可执行本地 Commit。

---

## 3. 分级规模决策

| 级别 | 判定标准 | 流程要求 |
|---|---|---|
| **S** | 单一文件或类内部重构，如重命名变量、提取短函数、内联无用委托 | 确保现有单测通过 $\to$ 局部重构 $\to$ 跑测与静态检测 $\to$ Commit。 |
| **M** | 跨类解耦、模块提炼、引入 GoF 设计模式集群、抽象防腐层（Adapter） | 建立特征测试网 $\to$ 模式选型与架构切片更新 $\to$ 渐进迁移 $\to$ 全量跑测与门禁。 |
| **L** | 核心架构分层迁移（如从泥球架构迁移到 Clean/Hexagonal/DDD）、微服务拆分 | 须建立双轨并行跑批（Shadow Run）验证，按 L 路径编制迁移阶段计划。 |
