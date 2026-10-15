---
name: hs-dev-discovery
description: Align new product requirements, real scenarios, scope, and expected behavior before detailed product design; owns BUILD phase 0, not technical selection or implementation.
license: MIT
---

# 需求理解与产品阶段编排

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

只编排阶段 0。产品规则归 product；不决定架构、不代签开发者预期、不启动所有领域 Skill。

## 输入

原始需求、真实使用案例、现状资料、约束与已有确认；沿用主路由给定的 intent/change_size。

## 执行

1. 核对已确认内容，缺少关键预期时执行开场对齐；不重复请求已明确的授权。
2. 先采集真实案例，再复述操作和结果；区分 CONFIRMED、DERIVED、OPEN，按返工代价关闭歧义。
3. 调用 product 功能 Skill 形成 DISC 对账、MVP 范围、PRD/原型及 PROD 证据；UI 专项按需交 frontend。
4. 详细规格仅覆盖已确认范围；关键能力未知时允许有边界的验证，不锁定完整技术栈。
5. 提交阶段 0 验收摘要；签收后把版本与未决项交回主路由，进入阶段 1，不能直接切编码。

## 输出与验收

需求预期对账、范围与假设表、PRD/适用原型、冻结基线与确认记录。

DISC/PROD 的通过条件由 product 清单规定；主 Skill 的阶段验收协议约束确认权限。

## 按需读取

- [opening_alignment](../../references/opening_alignment.md)
- [grill_orchestration](../../references/grill_orchestration.md)
- [confidence_decision](../../references/confidence_decision.md)
