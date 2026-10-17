# 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

**何时读**：处理阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 4：任务拆解与上下文装载 (Task Breakdown & Context Assembly)

### 1. 核心目标
将经过评审的详细设计拆解为独立、原子、可验证的工程任务项，通过渐进式四级路由 / SQLite 检索，将各阶段的**机器执行契约切片**物化装配进 `_05_task_orchestration/_03_task_context_pack/{task_id}_context_pack.md`，充当面向 VibeCoding 的极速装载包。

### 2. Context Pack 机器装配法则 (VibeCoding Assembly Rules)
1. **产品与 UI 契约**：优先装入阶段 0 的 **`{feature}_vibe_spec.md` 机器契约切片**（Design Tokens、组件树 DOM 骨架、状态机、Gherkin DoD），严禁整篇灌入人类版故事与讨论；
2. **选型与架构契约**：仅装入阶段 1/2 文档顶部的 **`[VIBE_CONTRACT]` 置顶切片**（仅占前几十行），跳过下半部废案讨论；
3. **实现四要素契约**：装入阶段 3 相关的局部表结构 SQL、API 契约或六元组方法签名切片；
4. **需求追踪链条装配 (Traceability Matrix)**：在 `task_detail.md` 中建立 `REQ-001..n` 到具体方法 Seam、自动化测试用例与验收证据的 100% 覆盖闭环，并在步骤清单标注执行策略（`[idempotent: true]`, `[retry: N]`, `[side_effect: local]`）；
5. 改代码/设计文件前：`python scripts/process_log.py checkpoint --id {task_id} --step … --summary "…" --paths …`（见 [`process_continuity.md`](../process_continuity.md)）。

---
