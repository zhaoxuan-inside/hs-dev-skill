---
name: hs-dev-governance
description: Apply shared document indexes, terminology, versioning, packaging, and explicitly enabled engineering governance controls; not automatically enabling CI/CD or operational infrastructure.
license: MIT
---

# 索引、版本、工程与运行治理

本 Skill 属于 hs-dev-skill 的功能轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

维护共享工程设施；不替产品裁剪功能，不替过程 Skill 推进阶段，READONLY 下禁止初始化或刷新索引。

## 输入

当前过程、已选工程约束、governance 配置、源文档与索引、明确授权范围。

## 执行

1. 核对目录、词典、索引与符号锚点，索引只是缓存，不能替代已验收源文档。
2. 按范围更新文档索引/罗盘和版本/产物说明；不因安装本 Skill 改写其他 Agent 配置。
3. 按 governance 开关应用机密、依赖和安全规则；CI/CD、遥测、数据韧性等默认不强加。
4. 远程规则仅在本地不足时按需读取，标注版本与证据；提交治理检查结果给当前过程。

## 输出与验收

适用的索引/词典、版本与产物记录、治理结果及需明确裁决的风险。

治理项按适用条件验收，不以配置齐全替代实际验证；push/发布仍需明确授权。

## 按需读取

- [auxiliary_governance](../../references/auxiliary_governance.md)
- [version_control](../../references/version_control.md)
- [four_level_routing](../../references/four_level_routing.md)
- [doc_reading_guide](../../references/doc_reading_guide.md)
- [learn_and_prefer](../../references/learn_and_prefer.md)
- [rule_library](../../references/rule_library.md)
