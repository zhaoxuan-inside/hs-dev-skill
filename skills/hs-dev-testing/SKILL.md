---
name: hs-dev-testing
description: Choose and run applicable behavior, contract, integration, regression, and quality checks; report evidence without declaring product acceptance or expanding implementation scope.
license: MIT
---

# 测试策略、执行与质量证据

本 Skill 属于 hs-dev-skill 的功能轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

负责质量证据；修复交 debugging/implementation，产品是否符合预期由开发者验收。

## 输入

REQ/场景基线、测试 seam、当前阶段、代码版本、环境和适用质量约束。

## 执行

1. 从需求与风险确定测试层级和反例，保持与实现结构独立的业务断言。
2. 实现期支持单行为红绿；交付期运行适用全量测试、静态检查与一致性检查，记录命令/环境/基线。
3. 区分 Mock 开发冒烟和真实集成验证，未运行/跳过/失败不得伪写 PASS。
4. 回收完整需求分母、DoD 证据和未实现清单，提交给当前过程或 acceptance。

## 输出与验收

测试规格、执行结果、覆盖映射、缺陷与限制，不输出人类验收结论。

保留既有适用门禁的零报错要求；EXPLORE 场景只读分析，不自动跑生成制品的命令。

## 按需读取

- [testing](../../references/testing.md)
- [quality_gates](../../references/quality_gates.md)
- [completion_audit](../../references/completion_audit.md)
