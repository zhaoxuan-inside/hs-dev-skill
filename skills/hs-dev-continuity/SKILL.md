---
name: hs-dev-continuity
description: Restore task context, assess requirement changes, invalidate affected acceptance, or roll back checkpoints; do not restart product discovery for a simple resume.
license: MIT
---

# 续做、变更与回退

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

负责恢复与变更影响；不直接替代 discovery/design 的业务与技术设计，不把恢复本身当交付完成。

## 输入

已有 plan/change 日志、任务与验收状态、源版本；变更时附开发者新表达。

## 执行

1. RESUME 先用 process_log resume-scan 恢复已确认目标、阶段、断点和未决项；不得把“继续”当新 BUILD。
2. 变更先区分理解偏差、需求变化或工程缺陷，评估文档/代码/测试与范围影响。
3. 按需要取得业务/DB/契约裁决，checkpoint 后更新源基线，使关联验收和派生 Pack 失效。
4. 回退仅针对指定快照和受影响路径，保留用户其他改动；遵守既有授权边界。
5. 把恢复后的阶段、有效确认、失效项和下一动作交回主路由，仅重验受影响项。

## 输出与验收

恢复/变更记录、有效/失效基线、明确的下一阶段及交接摘要。

不能丢失先前目标或重复询问已确认事项；完成状态必须有当前版本的有效验收。

## 按需读取

- [process_continuity](../../references/process_continuity.md)
- [requirement_change](../../references/requirement_change.md)
