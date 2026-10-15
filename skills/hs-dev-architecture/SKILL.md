---
name: hs-dev-architecture
description: Design technical choices, system boundaries, module responsibilities, runtime views, and justified patterns within accepted product constraints; not product scope or delivery approval.
license: MIT
---

# 技术选型、架构与模式

本 Skill 属于 hs-dev-skill 的功能轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

跨模块边界归本 Skill；前端局部结构归 frontend，后端局部结构归 backend，阶段推进归 design。

## 输入

产品/质量约束、当前阶段、既有 ADR、现有工程与风险。

## 执行

1. 按规模和项目类型选择范式，先比较约束匹配与复杂度，不默认 DDD 或微服务。
2. 选型明确候选、证据、代价和退出成本；影响承诺的未知项做最小验证。
3. 定义边界、模块职责、数据所有权、运行/部署协作及依赖方向，按需让前后端补专业视图。
4. 模式仅解决已识别问题；复杂协作按既有模式集群规范落盘，输出顶部执行契约。

## 输出与验收

当前阶段的 ADR、架构视图、机器约束和风险处理建议。

对照 TECH/ARCH 项提供证据，重要取舍交开发者；不自签，不替其他领域规定实现细节。

## 按需读取

- [dev_paradigm](../../references/dev_paradigm.md)
- [deep_modules](../../references/deep_modules.md)
- [ddd_design](../../references/ddd_design.md)
- [design_patterns](../../references/design_patterns.md)
