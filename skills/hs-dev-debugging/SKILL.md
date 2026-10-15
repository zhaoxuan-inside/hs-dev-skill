---
name: hs-dev-debugging
description: Diagnose and fix an observed defect through reproducible evidence, root-cause hypotheses, regression tests, and narrow repair; not speculative refactoring or new features.
license: MIT
---

# 缺陷诊断与修复

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

拥有 FIX 的推进顺序；专业修复由实际触达领域承担，不在诊断阶段顺便做结构重写。

## 输入

实际报错/现象、预期行为、复现条件、运行日志及受影响代码。

## 执行

1. 收集事实并构造最小复现；区分环境、数据、契约和代码问题。
2. 提出可证伪根因假设，先取得失败证据，再选择触达的功能 Skill 定位和修复。
3. 先红后绿，围绕根因最小修改；扩大范围需说明必要性，产品预期不明交 discovery。
4. 由 testing 验证回归与相关边界，更新触达契约和缺陷记录。
5. 按规模提交修复证据与验收；不重建未受影响的 PRD、选型或架构。

## 输出与验收

复现与根因证据、修复 diff、回归测试、同步契约及验收记录。

错误行为确实被原用例捕获、修复后通过且相关行为没有退化；最终确认遵循阶段验收协议。

## 按需读取

- [systematic_debugging](../../references/systematic_debugging.md)
