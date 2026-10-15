---
name: hs-dev-exploration
description: Explain existing code, architecture, or business flows with read-only search and evidence; no task scaffolding, product freeze, state changes, or commits.
license: MIT
---

# 只读理解与分析

本 Skill 属于 hs-dev-skill 的过程轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

EXPLORE 不走交付流水线，咨询不升级成实施；若用户随后要求修改，返回主 Skill 重新判路由。

## 输入

具体问题、相关代码/文档及只读访问范围。

## 执行

1. 锁定问题与目标范围，使用既有索引或精准文件搜索定位证据。
2. 只读调用触达的功能 Skill 解释专业含义，沿入口、编排、出口追踪。
3. 区分代码事实和推测，用必要的时序/状态/数据流及位置说明结论。
4. 直接返回答案；不运行初始化、任务创建、checkpoint、归档或 commit。

## 输出与验收

结论、代码/文档证据与必要图示，明确尚未证实的判断。

READONLY 贯穿子 Skill 调用；不能因为 testing 或 governance 的默认流程触发写操作。

## 按需读取

- [code_exploration](../../references/code_exploration.md)
