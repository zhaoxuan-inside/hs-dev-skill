---
name: hs-dev-acceptance
description: Collect and review evidence against stage acceptance criteria at any checkpoint or BUILD phase 6; never replace developer sign-off with model self-assessment.
license: MIT
---

# 阶段验收与交付判定

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

只负责证据审查和验收编排；不编写缺失功能、不代签、不把测试全绿直接等同产品符合预期。

## 输入

待验收阶段、输入/产出版本、适用 checklist、实际证据和已有开发者确认。

## 执行

1. 按当前阶段选 DISC/PROD 或 TECH/ARCH/DETAIL/TASK/IMPL/DELIV；验收工作状态与任务状态分开。
2. 逐项核对适用性、通过标准、来源版本、反例与证据；NA 记录理由，不能平均打分抵消失败。
3. 运行项交 testing，专项安全/版本/产物项交 governance；工具结果不能替代业务确认。
4. Agent 只提交 SUBMITTED 和候选结果；复用已有明确确认，缺少开发者验收时保留待验收。
5. 阶段 6 回收冻结需求分母、测试报告、未实现与自验说明；全部符合才归档及本地提交，push 需明确授权。

## 输出与验收

逐项验收记录、问题与偏差清单、确认记录；阶段 6 另含交付报告。

当前 CLI 尚未硬校验签收真实性；路由、测试或状态命令成功均不自动得到 ACCEPTED。

## 按需读取

- [stage_acceptance](../../references/stage_acceptance.md)
- [engineering_acceptance](../../references/engineering_acceptance.md)
- [standards_basis](../../references/standards_basis.md)
