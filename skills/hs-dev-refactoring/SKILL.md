---
name: hs-dev-refactoring
description: Refactor existing structure while preserving observable behavior using characterization tests and incremental equivalence checks; excludes feature changes and unresolved bug diagnosis.
license: MIT
---

# 行为保持的结构重构

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

只编排 REFACTOR；不以新增功能之名跳过保护网，也不以重构名义改公开语义。

## 输入

结构问题、现有行为/契约、拟改善目标、调用范围及测试保护网。

## 执行

1. 界定要保持的外部行为和要改善的结构，保护网不足先补特征测试。
2. 由 architecture/相关功能 Skill 比较重组方案；不为模式而增加结构。
3. 逐步迁移并验证等价，通用方法先查重，禁止混入产品功能变更。
4. 更新契约画像、调用链和索引；testing 检查保护网及回归。
5. 提交行为等价证据和结构改进说明，验收后归档。

## 输出与验收

重构计划、等价证据、结构变化、同步契约及回归结果。

现有合法外部行为保持；若发现原行为本身有缺陷，明确交 debugging，不能静默改变。

## 按需读取

- [code_refactoring](../../references/code_refactoring.md)
