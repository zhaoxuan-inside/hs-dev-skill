---
name: hs-dev-backend
description: Design or implement backend modules, database constraints, APIs, method contracts, adapters, and mock profiles for the selected process; not unapproved product rules.
license: MIT
---

# 后端、数据与接口契约

本 Skill 属于 hs-dev-skill 的功能轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

后端局部设计归本 Skill；跨模块架构边界交 architecture，业务空白交 product，完成判定交 acceptance。

## 输入

当前过程、业务规则、系统边界、数据/API 基线与环境约束。

## 执行

1. 明确业务不变量、数据归属和事务边界；新增/修改物理 DB 设计须按既有规则提交开发者决策。
2. 详细设计定义字段约束、访问模式、API Schema/错误、方法画像与调用链；只设计触达面。
3. 实现阶段通过 Adapter 隔离外部依赖，明确重复请求、超时、重试和部分失败的结果。
4. 通用方法先意图检索；六元组按适用画像使用，不强塞给所有轻量逻辑；同步迁移、契约和测试。

## 输出与验收

按阶段输出后端/DB/API/方法契约、实现、迁移与测试输入。

提供 DETAIL/IMPL 对应证据，Java 适用项见工程清单；Mock 不能证明真实集成，数据/契约关键取舍不能代签。

## 按需读取

- [backend_arch](../../references/backend_arch.md)
- [api_engineering](../../references/api_engineering.md)
- [method_archetypes](../../references/method_archetypes.md)
- [six_tuple_runtime](../../references/six_tuple_runtime.md)
- [mock_contract_guide](../../references/mock_contract_guide.md)
