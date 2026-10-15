---
name: hs-dev-design
description: Orchestrate BUILD phases 1-3 using accepted product inputs; select technical, architecture, and contract specialists without implementing code or redoing product discovery.
license: MIT
---

# 选型、架构与详细设计编排

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

拥有阶段顺序与交接；专业设计规则分别归 architecture/backend/frontend，验收裁定归 acceptance。

## 输入

当前阶段 1/2/3、有效产品基线、已确认约束、已有 ADR 与风险证据。

## 执行

1. 检查输入验收和版本；基线失效先交 continuity 处理影响，不能继续使用旧 Pack。
2. 阶段 1 调 architecture 比较选型并形成 ADR；阶段 2 由 architecture 定边界，按需让前后端补专业视图。
3. 阶段 3 调 backend 形成 DB/API/方法契约；触 UI 时调 frontend。只补触达面。
4. 按 TECH/ARCH/DETAIL 对应项准备证据，重要选型、DB 与契约决策沿用既有明确确认。
5. 每阶段验收后交回主路由；产品语义未决交 continuity 回切 discovery，禁止工程细节默定业务。

## 输出与验收

当前阶段设计文档、机器契约、决策/风险及有效验收记录；不是实现代码。

引用 [工程验收清单](../../references/engineering_acceptance.md) 当前节，不能因目录齐套自行放行。

## 按需读取

- 本过程无独占专业详规；按当前阶段借用 [工程验收清单](../../references/engineering_acceptance.md) 对应节，由选中的功能 Skill 提供设计细则。
