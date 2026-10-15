---
name: hs-dev-reverse
description: Onboard an existing project by reconstructing observed schemas, interfaces, terminology, and indexes with developer-validated boundaries; not building a new product or changing behavior.
license: MIT
---

# 存量工程逆向纳管

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

REVERSE 的目标是可靠描述现状；不擅自重构、迁移数据库或建立全新产品规格。

## 输入

现有代码与部署资料、优先域、已知限制和开发者指定的纳管范围。

## 执行

1. 先对齐优先域、不能改动的模块、术语与验收口径。
2. 按实际资产提取技术栈、DB/API、依赖和调用链；标注事实、推导及未决项。
3. 按触达领域调用 architecture/backend/frontend；只描述可证实行为，不把理想设计写成现状。
4. 用共享工具建立必要文档、词典、索引和罗盘，开发者核对关键边界和业务解释。
5. 执行纳管范围内一致性与验收，后续功能修改返回主路由另判 intent。

## 输出与验收

现状契约、边界/词典、必要索引、差异与未决项、纳管验收。

事实有代码或环境证据，业务推导有明确确认；不为纳管改变运行行为。

## 按需读取

- [reverse_engineering](../../references/reverse_engineering.md)
