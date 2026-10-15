---
name: hs-dev-planning
description: Break accepted designs into traceable tasks, dependencies, and version-bound context packs for BUILD phase 4; not product roadmap discovery or code implementation.
license: MIT
---

# 任务拆解与上下文装配

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

只分配已确认范围；全局产品分期由 product 负责，不在拆任务时自行增删功能。

## 输入

已验收设计、必需 REQ/场景基线、风险、可执行环境和当前阶段。

## 执行

1. 逐项把必需需求分配到任务和验收责任，防止漏项与重复归属。
2. 按可观察业务结果拆垂直切片，定义输入、输出、依赖、DoD、seam 与演练点。
3. Context Pack 只物化相关机器契约，记录源路径、版本/内容摘要和验收记录；先关闭可能推翻后续工作的风险。
4. 使用共享 task_manager 创建/维护任务；合法状态迁移与验收通过分别核对。
5. 按 TASK 项提交计划验收，通过后将可执行切片交 implementation。

## 输出与验收

任务清单、需求映射、依赖、有效 Context Pack、计划验收。

[工程清单 TASK](../../references/engineering_acceptance.md#5-阶段-4任务与上下文)逐项有证据；S 不造空任务包。

## 按需读取

- [task_state_machine](../../references/task_state_machine.md)
