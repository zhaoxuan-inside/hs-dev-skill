---
name: hs-dev-implementation
description: Implement accepted tasks with vertical red-green-refactor, synchronized contracts, and evidence for BUILD phase 5; excludes unresolved product design and independent bug diagnosis.
license: MIT
---

# 按已验收契约实现切片

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

只执行已验收任务；FIX 先走 debugging，REFACTOR 先走 refactoring，不混用新建产品流水线。

## 输入

有效任务/Pack、验收基线、代码现状、适用功能 Skill 和测试 seam。

## 执行

1. 核对 Pack 来源版本与任务 DoD；发现业务空白交 continuity，不以实现方便改变预期。
2. 改动前按既有 process_log checkpoint 保存可回退记录；通用方法先做意图查重。
3. 由触达的 frontend/backend 执行专业实现；testing 提供适用红绿和集成验证，单次围绕一个行为。
4. 同步代码、契约、迁移及测试；按风险演练真实业务切片，关闭差异后再扩展同类功能。
5. 提交 IMPL 证据与切片验收，再由主路由进入下一片或交付验收；未测不得称完成。

## 输出与验收

代码及同步文档、测试结果、切片演练、偏差记录和 IMPL 验收。

遵循 [IMPL 清单](../../references/engineering_acceptance.md#6-阶段-5实现切片)；实际交付门禁由 acceptance 编排。

## 按需读取

- [coding_standards](../../references/coding_standards.md)
